from app.agents.base_agent import BaseAgent
from app.core.state import AgentState

WRITER_PROMPT = """You are a writer agent. Given research notes, produce a clear,
well-structured draft answering the original task. Write for a general audience."""

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="writer", system_prompt=WRITER_PROMPT)

    def run(self, state: AgentState) -> AgentState:
        response = self.llm.invoke([
            ("system", self.system_prompt),
            ("human", f"Task: {state['task']}\n\nResearch notes:\n{state['research_notes']}"),
        ])
        state["draft"] = response.content
        state["iteration"] += 1
        return state