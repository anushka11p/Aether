from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.coder import CoderAgent
from app.agents.critic import CriticAgent

MAX_ITERATIONS = 6

researcher = ResearcherAgent()
writer = WriterAgent()
coder = CoderAgent()
critic = CriticAgent()

def researcher_node(state: AgentState) -> AgentState:
    return researcher.run(state)

def writer_node(state: AgentState) -> AgentState:
    return writer.run(state)

def coder_node(state: AgentState) -> AgentState:
    return coder.run(state)

def critic_node(state: AgentState) -> AgentState:
    return critic.run(state)

CODE_KEYWORDS = ["code", "script", "program", "function", "python", "algorithm", "write a", "calculate"]

def route_after_researcher(state: AgentState) -> str:
    task_lower = state["task"].lower()
    if any(kw in task_lower for kw in CODE_KEYWORDS):
        return "coder"
    return "writer"

def route_after_critic(state: AgentState) -> str:
    if state["iteration"] >= MAX_ITERATIONS:
        return "end"
    return state["next_agent"]

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("coder", coder_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("researcher")
    graph.add_conditional_edges("researcher", route_after_researcher, {
        "writer": "writer",
        "coder": "coder",
    })
    graph.add_edge("writer", "critic")
    graph.add_edge("coder", "critic")
    graph.add_conditional_edges("critic", route_after_critic, {
        "writer": "writer",
        "coder": "coder",
        "end": END,
    })

    return graph.compile()