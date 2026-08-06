from typing import TypedDict, Optional

class AgentState(TypedDict):
    task: str
    research_notes: Optional[str]
    draft: Optional[str]
    critique: Optional[str]
    final_output: Optional[str]
    iteration: int
    next_agent: Optional[str]
    search_succeeded: bool