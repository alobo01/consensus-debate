from typing import Dict, List, Optional
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ConsensusCrew1:
	"""ConsensusCrew crew Stage 1-3"""

	# Configuration file paths
	agents_config_path = 'config/agents.yaml'
	tasks_config_path = 'config/tasks.yaml'

	# Default model (can be overridden per agent)
	default_model = "ollama/llama3.2"
	# Example of per-agent models
	# models = {
	#	 "FreeMarketProponent": "ollama/qwen1.5", 
	#	 "GovernmentInterventionAdvocate": "ollama/llama3.1"
	# }

	agents_verbose = True

	def __init__(self, agents_list, global_tasks, models=None, *args, **kwargs):
		"""
		Initialize the ConsensusCrew1 with specific agents and tasks.

		Args:
			agents_list (list): List of agent identifiers.
			global_tasks (list): List of global task identifiers.
			models (dict or str, optional): Model configurations per agent or a default model.
		"""
		super().__init__(*args, **kwargs)  # Ensure proper initialization of the base class
		self.agents_list = agents_list
		self.global_tasks = global_tasks
		self.models = models if models is not None else self.default_model
		self.load_configurations()


	@crew
	def crew(self) -> Crew:
		"""Creates the ConsensusCrew crew with specified agents and tasks."""
		agents = []
		tasks = []
		agents_map = {}

		# Initialize Agents
		for agent_id in self.agents_list:
			# Determine the model for the agent
			if isinstance(self.models, dict):
				model = self.models.get(agent_id, self.default_model)
			else:
				model = self.models

			agent_config = self.agents_config.get(agent_id)
			if not agent_config:
				raise ValueError(f"Agent configuration for '{agent_id}' not found.")

			# Create LLM instance if "llm" is not specified in the agent config
			if "llm" not in agent_config:
				llm_instance = LLM(model=model, base_url="http://localhost:11434",timeout=6000)
				agent = Agent(
					config=agent_config,
					llm=llm_instance,
					verbose=self.agents_verbose
				)
			else:
				agent = Agent(
					config=agent_config,
					verbose=self.agents_verbose
				)

			agents.append(agent)
			agents_map[agent_id] = agent

		# Initialize Tasks
		for task_id in self.global_tasks:
			task_config = self.tasks_config.get(task_id)
			task_list_context = []
			if task_config is None:
				raise ValueError(f"Task configuration for '{task_id}' not found.")
			
			for agent_id in self.agents_list:
				if agent_id != "reporting_analyst":
					agent = agents_map.get(agent_id)
					if not agent:
						raise ValueError(f"Agent '{agent_id}' not found for task '{task_id}'.")
					task = Task(
						config=task_config,
						agent=agent
					)
					tasks.append(task)
					task_list_context.append(task)

			# Add Reporting Task
			reporting_task_config = self.tasks_config.get('reporting_task')
			if not reporting_task_config:
				raise ValueError("Reporting task configuration 'reporting_task' not found.")

			reporting_agent = agents_map.get("reporting_analyst")
			if not reporting_agent:
				raise ValueError("Agent 'reporting_analyst' not found.")

			reporting_task = Task(
				config=reporting_task_config,
				agent=reporting_agent,
				context=task_list_context
			)
			tasks.append(reporting_task)

		return Crew(
			agents=agents,
			tasks=tasks,
			process=Process.sequential,
			verbose=True,
			# Uncomment the below line to use hierarchical processing instead
			# process=Process.hierarchical,
		)
	

@CrewBase
class ConsensusCrew2:
	"""ConsensusCrew crew Stage 4-6"""

	# Configuration file paths
	agents_config_path = 'config/agents.yaml'
	tasks_config_path = 'config/tasks.yaml'

	# Default model (can be overridden per agent)
	default_model = "ollama/llama3.2"
	# Example of per-agent models
	# models = {
	#	 "FreeMarketProponent": "ollama/qwen1.5", 
	#	 "GovernmentInterventionAdvocate": "ollama/llama3.1"
	# }

	agents_verbose = True

	def __init__(self, agents_list, global_tasks, models=None, *args, **kwargs):
		"""
		Initialize the ConsensusCrew1 with specific agents and tasks.

		Args:
			agents_list (list): List of agent identifiers.
			global_tasks (list): List of global task identifiers.
			models (dict or str, optional): Model configurations per agent or a default model.
		"""
		super().__init__(*args, **kwargs)  # Ensure proper initialization of the base class
		self.agents_list = agents_list
		self.global_tasks = global_tasks
		self.models = models if models is not None else self.default_model
		self.load_configurations()


	@crew
	def crew(self) -> Crew:
		"""Creates the ConsensusCrew crew with specified agents and tasks."""
		agents = []
		tasks = []
		agents_map = {}

		# Initialize Agents
		for agent_id in self.agents_list:
			# Determine the model for the agent
			if isinstance(self.models, dict):
				model = self.models.get(agent_id, self.default_model)
			else:
				model = self.models

			agent_config = self.agents_config.get(agent_id)
			if not agent_config:
				raise ValueError(f"Agent configuration for '{agent_id}' not found.")

			# Create LLM instance if "llm" is not specified in the agent config
			if "llm" not in agent_config:
				llm_instance = LLM(model=model, base_url="http://localhost:11434",timeout=6000)
				agent = Agent(
					config=agent_config,
					llm=llm_instance,
					verbose=self.agents_verbose
				)
			else:
				agent = Agent(
					config=agent_config,
					verbose=self.agents_verbose
				)

			agents.append(agent)
			agents_map[agent_id] = agent


		task_list_context = []
		
		# Initialize first task
		task_config = self.tasks_config.get(self.global_tasks[0])
		for agent_id in self.agents_list:
			if agent_id != "reporting_analyst":
				agent = agents_map.get(agent_id)
				task = Task(config=task_config, agent=agent)
				task_list_context.append(task)

		tasks = []
		# Initialize subsequent tasks
		for task_id in self.global_tasks[1:]:
			task_config = self.tasks_config.get(task_id)
			for agent_id in self.agents_list:
				if agent_id != "reporting_analyst":
					agent = agents_map.get(agent_id)
					task = Task(config=task_config, agent=agent, context=task_list_context)
					tasks.append(task)
			
			task_list_context = tasks
			tasks = []
			

		# Add Reporting Task
		reporting_task_config = self.tasks_config.get('reporting_task')
		reporting_agent = agents_map.get("reporting_analyst")
		reporting_task = Task(
			config=reporting_task_config,
			agent=reporting_agent,
			context=task_list_context
		)
		tasks.append(reporting_task)

		return Crew(
			agents=agents,
			tasks=tasks,
			process=Process.sequential,
			verbose=True,
			# Uncomment the below line to use hierarchical processing instead
			# process=Process.hierarchical,
		)
	
@CrewBase
class ConsensusCrew:
	"""Generalized ConsensusCrew for executing before, debater, between, and after tasks."""

	# Configuration file paths
	agents_config_path = 'config/agents.yaml'
	tasks_config_path = 'config/tasks.yaml'

	# Default model (can be overridden per agent)
	default_model = "ollama/llama3.2"
	# Example of per-agent models
	# models = {
	#	 "FreeMarketProponent": "ollama/qwen1.5", 
	#	 "GovernmentInterventionAdvocate": "ollama/llama3.1"
	# }

	agents_verbose = True

	def __init__(self, 
				 debaters_agents_list: List[str], 
				 core_agents_list: List[str], 
				 before_tasks: List[str],
				 debaters_tasks: List[str],
				 between_tasks: List[str],
				 after_tasks: List[str],
				 models: Optional[Dict[str, str]] = None, 
				 *args, 
				 **kwargs):
		"""
		Initialize the ConsensusCrew with specific agents and task phases.

		Args:
			agents_list (list): List of debater agent identifiers.
			before_tasks (list): List of before task identifiers.
			debater_tasks (list): List of debater task identifiers.
			between_tasks (list): List of between task identifiers.
			after_tasks (list): List of after task identifiers.
			models (dict or str, optional): Model configurations per agent or a default model.
		"""
		
		super().__init__(*args, **kwargs)  # Ensure proper initialization of the base class
		self.debaters_agents = debaters_agents_list
		self.core_agents = core_agents_list
		self.before_tasks = before_tasks
		self.debaters_tasks = debaters_tasks
		self.between_tasks = between_tasks
		self.after_tasks = after_tasks
		self.models = models if models is not None else self.default_model
		self.load_configurations()

	@crew
	def crew(self) -> Crew:
		"""Creates the ConsensusCrew with specified agents and tasks phases."""
		agents = []
		agents_map = {}

		# Initialize Agents
		for agent_id in self.debaters_agents+self.core_agents:
			# Determine the model for the agent
			if isinstance(self.models, dict):
				model = self.models.get(agent_id, self.default_model)
			else:
				model = self.models

			agent_config = self.agents_config.get(agent_id)
			if not agent_config:
				raise ValueError(f"Agent configuration for '{agent_id}' not found.")

			# Create LLM instance if "llm" is not specified in the agent config
			if "llm" not in agent_config:
				llm_instance = LLM(model=model, base_url="http://localhost:11434", timeout=6000) # Timeout in seconds, my laptop is so slow :(
				agent = Agent(
					config=agent_config,
					llm=llm_instance,
					verbose=self.agents_verbose
				)
			else:
				agent = Agent(
					config=agent_config,
					verbose=self.agents_verbose
				)

			agents.append(agent)
			agents_map[agent_id] = agent



		tasks = []

		# Execute Before Tasks
		for agent_id,task_id in self.before_tasks:
			task_config = self.tasks_config.get(task_id)
			agent = agents_map.get(agent_id)
			if not task_config:
				raise ValueError(f"Before task configuration for '{task_id}' not found.")
			task = Task(
				config=task_config,
				agent=agent
			)
			tasks.append(task)

		# Initialize context for debater tasks
		debater_context = tasks.copy()

		# Execute Debater Tasks with Between Tasks
		for idx, debater_task_id in enumerate(self.debaters_tasks):
			# Initialize Debater Tasks
			debater_tasks_current = []
			for agent_id in self.debaters_agents:
				agent = agents_map.get(agent_id)
				if not agent:
					raise ValueError(f"Debater agent '{agent_id}' not found.")
				task_config = self.tasks_config.get(debater_task_id)
				if not task_config:
					raise ValueError(f"Debater task configuration for '{debater_task_id}' not found.")
				task = Task(
					config=task_config,
					agent=agent,
					context=debater_context  # Pass previous debater tasks as context
				)
				debater_tasks_current.append(task)
				tasks.append(task)

			# Update context with current debater tasks
			debater_context = debater_tasks_current.copy()
			# Execute Between Tasks after each debater task phase, except after the last debater task
			if idx < len(self.debaters_tasks) - 1:
				debater_tasks_current = []
				for agent_id,between_task_id in self.between_tasks:
					between_task_config = self.tasks_config.get(between_task_id)
					agent = agents_map.get(agent_id)
					if not between_task_config:
						raise ValueError(f"Between task configuration for '{between_task_id}' not found.")
					between_task = Task(
						config=between_task_config,
						agent=agent,
						context=debater_context  # Pass current debater tasks as context
					)
					debater_tasks_current.append(between_task)
					tasks.append(between_task)
				debater_context = debater_tasks_current.copy()

		# Execute After Tasks
		for agent_id,after_task_id in self.after_tasks:
			after_task_config = self.tasks_config.get(after_task_id)
			agent = agents_map.get(agent_id)
			if not after_task_config:
				raise ValueError(f"After task configuration for '{after_task_id}' not found.")
			after_task = Task(
				config=after_task_config,
				agent=agent,
				context=debater_context  # Pass the last debater tasks as context
			)
			tasks.append(after_task)

		return Crew(
			agents=agents,
			tasks=tasks,
			process=Process.sequential,  # Adjust as needed (sequential or hierarchical)
			verbose=True,
		)

def main():
	# Define your agents and tasks lists
	debaters_agents = [
		"FreeMarketProponent",
		"GovernmentInterventionAdvocate",
		"CentristMediator",
	]

	core_agents = [
		"reporting_analyst",
		"judging_agent",
	]

	# Configuration of stages with their respective tasks
	stagesConfig =[
		{
			"before": [],
			"between": [("reporting_analyst", "reporting_task")],
			"after": [("reporting_analyst", "reporting_task")],
			"debaters_tasks": [
				"identify_key_questions_task",
				"analyze_potential_impacts_task",
				"propose_possible_solutions_task",
				"evaluate_feasibility_task"
			],
		},
		{
			"before": [("judging_agent", "formulate_proposal_task")],
			"between": [],
			"after": [("judging_agent", "integrate_amends_task")],
			"debaters_tasks": ["amend_proposal_task"],
		},
		{
			"before": [],
			"between": [],
			"after": [("judging_agent", "recopilate_and_evaluate_task")],
			"debaters_tasks": ["collect_agent_responses_task"],
		},
		{
			"before": [],
			"between": [],
			"after": [("reporting_analyst", "generate_consensus_report_task")],
			"debaters_tasks": ["collect_agent_responses_task"],
		},
	]



	# Define the list of models based on your 'ollama list' output
	models = [
		# "ollama/falcon3:10b",
		# "ollama/falcon3:latest",
		"ollama/llama3.2:latest",
		# "ollama/llama3.1:latest"
	]

	N_REPETITIONS = 1

	# Iterate through each model
	for model in models:
		# Initialize a list to hold kickoff results for the current model
		kickoff_results = []

		for run_number in range(1, 1 + N_REPETITIONS):  # Repeat kickoff N_REPETITIONS times
			try:
				result = ""
				for stage_id, stage in enumerate(stagesConfig, start=1):
					consensus_crew = ConsensusCrew(
						core_agents_list=core_agents,
						debaters_agents_list=debaters_agents,
						before_tasks=stage["before"],
						debater_tasks=stage["debaters_tasks"],
						between_tasks=stage["between"],
						after_tasks=stage["after"],
						models=model
					)
					result = consensus_crew.crew().kickoff({
						"topic": "General Basic Income",
						"agents": str(debaters_agents),
						"result": result
					})

					result = result.raw
					kickoff_results.append({
						"run": run_number,
						"result": result,
						"stage_id": stage_id
					})
			except Exception as e:
				print(f"Error occurred for model {model} in run {run_number}: {e}")

		# Generate Markdown content for the current model
		markdown_content = f"# Consensus Crew Kickoff Results for Model: {model}\n\n"
		for entry in kickoff_results:
			markdown_content += f"**Run {entry['run']}**\n\n"
			markdown_content += f"**Stage {entry['stage_id']}**\n\n"
			markdown_content += f"{entry['result']}\n\n"

		# Define the output Markdown file path for the current model
		sanitized_model_name = model.replace(":", "_").replace("/", "_")
		output_file = f"consensus_kickoff_results_{sanitized_model_name}.md"

		# Write the Markdown content to the file
		with open(output_file, "w", encoding="utf-8") as md_file:
			md_file.write(markdown_content)

		print(f"Kickoff results for model {model} have been saved to {output_file}")

if __name__ == "__main__":
	main()