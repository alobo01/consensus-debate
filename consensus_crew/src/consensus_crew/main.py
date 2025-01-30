import json
from crewai.flow.flow import Flow, start, listen
from crewai import completion
import yaml
from consensus_crew.src.consensus_crew.crews import ConsensusCrew

def load_config(config_path: str = "crew_config.yaml"):
    """Loads entire configuration (agents, tasks, stagesConfig, etc.) from YAML."""
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data
################################################################################
# 4) Flow example that orchestrates the 4 crews,
#    handles stage 6 output, and can re-run the second config if needed.
################################################################################

class ConsensusOrchestrationFlow(Flow):
    """
    Demonstrates a flow that:
      1) Runs CrewStages1to3 => stages 1-3
      2) Runs CrewStages4to5 => stages 4-5
      3) Runs CrewStage6 => stage 6
         - Checks the JSON output for possible 'problems'
         - If needed, re-run CrewStages4to5 up to 'max_retries'
      4) Runs CrewStage7 => stage 7
    """

    def __init__(self, config_path="crew_config.yaml", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_data = load_config(config_path)
        self.stages_config = self.config_data["stagesConfig"]
        self.topic = self.config_data.get("topic", "General Basic Income")
        self.models = self.config_data.get("models", ["ollama/llama3.2:latest"])
        self.max_retries = self.config_data.get("max_retries", 5)
        self.stage6_output=""
        self.retries=0

    @start()
    def run_stages_1_to_3(self):
        """Kick off stages 1-3 using CrewStages1to3."""
        crew13 = ConsensusCrew(
            debaters_agents_list=self.config_data["debaters_agents"],
            core_agents_list=self.config_data["core_agents"],
            after_tasks=self.config_data["stageConfig"][0]["after"],
            before_tasks=self.config_data["stageConfig"][0]["before"],
            between_tasks=self.config_data["stageConfig"][0]["between"],
            debater_tasks=self.config_data["stageConfig"][0]["debater_tasks"],
            model=self.models[0]
        )
        # The initial "prompt_data" can include the topic
        kickoff_result = crew13.crew().kickoff({
            "topic": self.topic,
            "agents": str(self.config_data["debaters_agents"]+self.config_data["core_agents"]),
        })
        return kickoff_result.raw  # pass forward the raw result as context

    @listen(or_(run_stages_1_to_3, "failedConsensus"))
    def run_stages_4_to_5(self, prev_result):
        """Run the second crew (stages 4-5)."""
        crew45 = ConsensusCrew(
            debaters_agents_list=self.config_data["debaters_agents"],
            core_agents_list=self.config_data["core_agents"],
            after_tasks=self.config_data["stageConfig"][1]["after"],
            before_tasks=self.config_data["stageConfig"][1]["before"],
            between_tasks=self.config_data["stageConfig"][1]["between"],
            debater_tasks=self.config_data["stageConfig"][1]["debater_tasks"],
            model=self.models[0]
        )
        result_45 = crew45.crew().kickoff({
            "failed_ideas": self.stage6_output,
            "topic": self.topic,
            "result": prev_result,
            "agents": str(self.config_data["debaters_agents"]+self.config_data["core_agents"]),
        })
        return result_45.raw

    @listen(run_stages_4_to_5)
    def run_stage_6(self, prev_result):
        """Run the third crew (stage 6). Then parse output to see if we need to re-run."""
        crew6 = ConsensusCrew(
            debaters_agents_list=self.config_data["debaters_agents"],
            core_agents_list=self.config_data["core_agents"],
            after_tasks=self.config_data["stageConfig"][2]["after"],
            before_tasks=self.config_data["stageConfig"][2]["before"],
            between_tasks=self.config_data["stageConfig"][2]["between"],
            debater_tasks=self.config_data["stageConfig"][2]["debater_tasks"],
            model=self.models[0]
        )
        stage_6_result = crew6.crew().kickoff({
            "topic": self.topic,
            "result": prev_result,
            "agents": str(self.config_data["debaters_agents"]+self.config_data["core_agents"]),
        })
        output_str = stage_6_result.raw

        # Attempt to parse JSON from the agent. 
        # (In reality, you may need more robust error handling)
        try:
            data = json.loads(output_str)
        except Exception as e:
            print("WARNING: Stage 6 output is not valid JSON. Error:", e)
            data = {}

        # Evaluate opinions using a Weighted stance approach
        # e.g. stance_value_map = { "Block": -1, "Have Reservations": -0.5, "Stand Aside": 0, "Support": +1 }
        # or read from data's stance. The example had "Have Reservations" with importance 8.

        # Example of generic mapping:
        stance_value_map = {
            "Block": -1.0,
            "Have Reservations": -0.5,
            "Stand Aside": 0.0,
            "Conditional Support": 0.5,
            "Support": 1.0,
        }

        # If the JSON includes "agents_opinions", parse them:
        agents_opinions = data.get("agents_opinions", [])
        total_score = 0.0
        total_importance = 0.0

        # For each opinion, find stance in the mapping or treat unknown stance as 0. 
        for opinion in agents_opinions:
            stance = opinion.get("stance", "").strip()
            importance = float(opinion.get("importance", 5))  # default to 5
            stance_val = stance_value_map.get(stance, 0.0)
            total_score += stance_val * importance
            total_importance += importance

        # Weighted stance formula
        # WeightedStance = sum( stance_value(agent) * importance(agent) ) / sum( importance(agent) )
        # Example threshold: if WeightedStance >= 0 => we interpret as "leaning to support"
        if total_importance > 0:
            weighted_stance = total_score / total_importance
        else:
            weighted_stance = 0.0
        
        print(f"DEBUG: Weighted stance from stage 6 = {weighted_stance:.2f}")

        # final decision or parse from the "final_decision" field
        final_decision = data.get("final_decision", {})
        accept_proposal = final_decision.get("accept_proposal", "false").lower() == "true"

        # In your strategy: if WeightedStance < 0 or agent's final decision says false => we treat it as a "problem"
        problem_detected = (weighted_stance < 0) or (not accept_proposal)

        return {
            "raw_output": output_str,
            "problem_detected": problem_detected
        }

    @listen(run_stage_6)
    def maybe_repeat_stages_4_to_5(self, stage_6_data):
        """
        If stage 6 indicates a problem, re-run CrewStages4to5 up to max_retries times.
        Then return the final result from stage 6 if no more changes happen.
        """
        problem_detected = stage_6_data["problem_detected"]
        raw_output = stage_6_data["raw_output"]
        self.stage6_output=raw_output
        if not problem_detected or self.retries==self.max_retries:
            # No need to re-run
            print("No problem detected in Stage 6; proceeding to Stage 7.")
            return "success"

        # If there's a problem, attempt re-runs up to max_retries times
        self.retries+=1
        return "failedConsensus"

        

    @listen("success")
    def run_stage_7(self, prev_result):
        """Finally run stage 7 (the fourth crew)."""
        
        crew7 = ConsensusCrew(
            debaters_agents_list=self.config_data["debaters_agents"],
            core_agents_list=self.config_data["core_agents"],
            after_tasks=self.config_data["stageConfig"][3]["after"],
            before_tasks=self.config_data["stageConfig"][3]["before"],
            between_tasks=self.config_data["stageConfig"][3]["between"],
            debater_tasks=self.config_data["stageConfig"][3]["debater_tasks"],
            model=self.models[0]
        )
        final_result = crew7.crew().kickoff({
            "topic": self.topic,
            "result": prev_result,
            "agents": str(self.config_data["debaters_agents"]+self.config_data["core_agents"]),
        })
        return final_result.raw

    # # Optionally, define a simple entry method to run the flow
    # def run_flow(self, topic="General Basic Income"):
    #     """
    #     Convenience method to run the entire flow from outside.
    #     """
    #     final_output = self.run_stages_1_to_3(topic=topic)
    #     final_output = self.run_stages_4_to_5(final_output)
    #     stage_6_data = self.run_stage_6(final_output)
    #     final_output = self.maybe_repeat_stages_4_to_5(stage_6_data)
    #     final_output = self.run_stage_7(final_output)
    #     return final_output


################################################################################
# 5) If you want a direct script entry, do:
################################################################################

if __name__ == "__main__":
    flow = ConsensusOrchestrationFlow(config_path="crew_config.yaml")
    result = flow.kickoff()
    print("==== FINAL OUTPUT (Stage 7) ====")
    print(result)