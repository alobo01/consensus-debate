from typing import List, Dict, Optional
from pydantic import BaseModel

# ----------------------
# STAGE 1: Introduce & Clarify
# ----------------------

class Stage1Input(BaseModel):
    topic: str
    background_info: Optional[str] = None

class Stage1AgentTaskOutput(BaseModel):
    agent_id: str
    understanding_of_issue: str
    scope_clarification: str
    questions_or_concerns: List[str]

class Stage1Output(BaseModel):
    aggregated_understanding: str
    all_questions: List[str]
    # We might also store each agent's output separately if needed
    agent_responses: List[Stage1AgentTaskOutput]

# ----------------------
# STAGE 2: Open Out the Discussion
# ----------------------

class Stage2Input(BaseModel):
    topic: str
    # Possibly carry over prior stage outputs
    stage1_output: Stage1Output

class Stage2AgentTaskOutput(BaseModel):
    agent_id: str
    personal_needs_or_goals: List[str]
    viewpoint_or_opinion: str

class Stage2Output(BaseModel):
    all_needs_and_goals: Dict[str, List[str]]  # Mapping agent_id -> needs/goals
    summary_of_opinions: str
    agent_responses: List[Stage2AgentTaskOutput]

# ----------------------
# STAGE 3: Explore Ideas
# ----------------------

class Stage3Input(BaseModel):
    topic: str
    stage2_output: Stage2Output

class Stage3AgentTaskOutput(BaseModel):
    agent_id: str
    proposed_idea: str
    pros: List[str]
    cons: List[str]

class Stage3Output(BaseModel):
    collected_ideas: List[str]
    analysis_of_ideas: str
    agent_responses: List[Stage3AgentTaskOutput]

# ----------------------
# STAGE 4: Form a Proposal
# ----------------------

class Stage4Input(BaseModel):
    topic: str
    stage3_output: Stage3Output

class Stage4AgentTaskOutput(BaseModel):
    agent_id: str
    # Each agent can suggest how to merge or refine ideas into a single proposal
    refined_proposal_elements: str

class Stage4Output(BaseModel):
    draft_proposal: str
    agent_responses: List[Stage4AgentTaskOutput]

# ----------------------
# STAGE 5: Amend the Proposal
# ----------------------

class Stage5Input(BaseModel):
    topic: str
    stage4_output: Stage4Output

class Stage5AgentTaskOutput(BaseModel):
    agent_id: str
    suggested_amendments: str
    rationale: str

class Stage5Output(BaseModel):
    amended_proposal: str
    agent_responses: List[Stage5AgentTaskOutput]

# ----------------------
# STAGE 6: Test for Agreement
# ----------------------

class Stage6Input(BaseModel):
    topic: str
    stage5_output: Stage5Output

class Stage6AgentTaskOutput(BaseModel):
    agent_id: str
    # Agents indicate their stance on the final proposal
    block: bool
    stand_aside: bool
    reservations: Optional[str]
    comments: Optional[str]

class Stage6Output(BaseModel):
    final_proposal: str
    agreement_summary: str
    # Could store how many blocks, stand-asides, etc.
    blocks: List[str]
    stand_asides: List[str]
    reservations: List[str]
    agent_responses: List[Stage6AgentTaskOutput]

# ----------------------
# STAGE 7: Implement the Decision
# ----------------------

class Stage7Input(BaseModel):
    topic: str
    stage6_output: Stage6Output

class ImplementationStep(BaseModel):
    step_description: str
    assigned_to: Optional[str]

class Stage7AgentTaskOutput(BaseModel):
    agent_id: str
    # Each agent might suggest steps for implementation
    implementation_suggestions: List[ImplementationStep]

class Stage7Output(BaseModel):
    final_implementation_plan: List[ImplementationStep]
    agent_responses: List[Stage7AgentTaskOutput]
