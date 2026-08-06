from app.core.llm_provider import get_llm
from app.core.state import AgentState

class BaseAgent:
    def __init__(self, name: str, system_prompt: str, temperature: float = 0.3):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = get_llm(temperature=temperature)

    def run(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Each agent must implement its own run()")