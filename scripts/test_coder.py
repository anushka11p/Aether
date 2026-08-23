import sys
sys.path.append("backend")

from app.agents.coder import CoderAgent
from app.core.state import AgentState

agent = CoderAgent()
state: AgentState = {
    "task": "Write Python code that calculates and prints the first 10 Fibonacci numbers.",
    "research_notes": None,
    "draft": None,
    "critique": None,
    "final_output": None,
    "iteration": 0,
    "next_agent": None,
    "search_succeeded": False,
}

result = agent.run(state)
print(result["draft"])