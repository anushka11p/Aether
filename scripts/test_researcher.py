import sys
sys.path.append("backend")

from app.agents.researcher import ResearcherAgent
from app.core.state import AgentState

agent = ResearcherAgent()
state: AgentState = {
    "task": "What are the key benefits of vector databases for AI memory?",
    "research_notes": None,
    "draft": None,
    "critique": None,
    "final_output": None,
    "iteration": 0,
    "next_agent": None,
}

result = agent.run(state)
print(result["research_notes"])