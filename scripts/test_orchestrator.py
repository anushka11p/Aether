import sys
sys.path.append("backend")

from app.agents.orchestrator import build_graph
from app.core.state import AgentState

graph = build_graph()

initial_state: AgentState = {
    "task": "Explain why vector databases matter for AI agent memory, in 3 short paragraphs.",
    "research_notes": None,
    "draft": None,
    "critique": None,
    "final_output": None,
    "iteration": 0,
    "next_agent": None,
}

result = graph.invoke(initial_state)

print("=== FINAL OUTPUT ===")
print(result["final_output"])
print(f"\n(Completed in {result['iteration']} agent steps)")