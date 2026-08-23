from app.agents.base_agent import BaseAgent
from app.core.state import AgentState
from app.tools.code_executor import execute_code

CODER_PROMPT = """You are a coder agent. Given a task, write a single self-contained
Python script that accomplishes it.

CRITICAL CONSTRAINTS:
- The script will run in a non-interactive subprocess with no stdin available.
- NEVER use input() or any function that waits for user input.
- If the task implies a specific example (e.g. "check if a number is prime"),
  hardcode a reasonable example value and print the result — do not prompt for it.
- Output ONLY the raw Python code, no markdown fences, no explanation.
"""

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coder", system_prompt=CODER_PROMPT)

    def run(self, state: AgentState) -> AgentState:
        response = self.llm.invoke([
            ("system", self.system_prompt),
            ("human", state["task"]),
        ])
        code = response.content.strip()

        result = execute_code(code)

        state["draft"] = (
            f"```python\n{code}\n```\n\n"
            f"**Output:**\n{result['stdout']}\n\n"
            f"**Errors:**\n{result['stderr'] if result['stderr'] else 'None'}"
        )
        state["iteration"] += 1
        return state
