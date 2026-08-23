from app.agents.base_agent import BaseAgent
from app.core.state import AgentState

CRITIC_PROMPT = """You are a critic agent. Review the output against the task.
If it is accurate, complete, and clear, respond starting with "APPROVE".
Otherwise respond starting with "REVISE" followed by specific, actionable feedback."""

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="critic", system_prompt=CRITIC_PROMPT)

    def run(self, state: AgentState) -> AgentState:
        response = self.llm.invoke([
            ("system", self.system_prompt),
            ("human", f"Task: {state['task']}\n\nOutput:\n{state['draft']}"),
        ])
        state["critique"] = response.content
        state["iteration"] += 1
        if response.content.strip().upper().startswith("APPROVE"):
            state["final_output"] = state["draft"]
            state["next_agent"] = "end"
        else:
            # Revise via whichever agent produced this draft
            state["next_agent"] = "coder" if "```python" in (state["draft"] or "") else "writer"
        return state