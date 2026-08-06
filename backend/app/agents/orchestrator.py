from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.critic import CriticAgent

MAX_ITERATIONS = 6  # guard against infinite revise loops

researcher = ResearcherAgent()
writer = WriterAgent()
critic = CriticAgent()

def researcher_node(state: AgentState) -> AgentState:
    return researcher.run(state)

def writer_node(state: AgentState) -> AgentState:
    return writer.run(state)

def critic_node(state: AgentState) -> AgentState:
    return critic.run(state)

def route_after_critic(state: AgentState) -> str:
    if state["iteration"] >= MAX_ITERATIONS:
        return "end"
    return state["next_agent"]

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", route_after_critic, {
        "writer": "writer",
        "end": END,
    })

    return graph.compile()