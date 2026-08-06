from app.agents.base_agent import BaseAgent
from app.core.state import AgentState
from app.memory.vector_store import query_memory
from app.tools.web_search import web_search

RESEARCHER_PROMPT = """You are a research agent. Given a task, produce concise,
factual notes that a writer agent can use. Do not write prose — output notes only.

You are given two sources of context:
1. "Relevant past context" — retrieved from prior runs by similarity search. This is
   NOT guaranteed to be relevant or correct. Only use it if it genuinely matches the
   current task; otherwise ignore it entirely.
2. "Live web search results" — current, real information from the web. Prefer this
   over your own internal knowledge for anything specific, niche, or fast-changing
   (libraries, tools, versions, current events). If your internal knowledge conflicts
   with the search results, trust the search results."""

class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="researcher", system_prompt=RESEARCHER_PROMPT)

    def run(self, state: AgentState) -> AgentState:
        past_context = query_memory(state["task"])
        context_block = "\n---\n".join(past_context) if past_context else "None."

        search_results, search_ok = web_search(state["task"])
        state["search_succeeded"] = search_ok

        response = self.llm.invoke([
            ("system", self.system_prompt),
            ("human",
                f"Task: {state['task']}\n\n"
                f"Relevant past context:\n{context_block}\n\n"
                f"Live web search results:\n{search_results}"),
        ])
        state["research_notes"] = response.content
        state["iteration"] = state.get("iteration", 0) + 1
        return state