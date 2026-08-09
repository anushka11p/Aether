from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.agents.orchestrator import build_graph
from app.core.state import AgentState
from app.core.database import get_session
from app.models.run import Run
from app.memory.vector_store import add_memory
from app.core.config import settings

router = APIRouter()
graph = build_graph()

@router.websocket("/ws/run")
async def websocket_run(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        if data.get("api_key") != settings.AETHER_API_KEY:
            await websocket.send_json({"type": "error", "message": "Unauthorized"})
            await websocket.close()
            return

        initial_state: AgentState = {
            "task": task,
            "research_notes": None,
            "draft": None,
            "critique": None,
            "final_output": None,
            "iteration": 0,
            "next_agent": None,
            "search_succeeded": False,
        }

        final_state = initial_state

        async for step in graph.astream(initial_state):
            node_name = list(step.keys())[0]
            node_state = step[node_name]
            final_state = node_state

            await websocket.send_json({
                "type": "step",
                "agent": node_name,
                "iteration": node_state.get("iteration"),
            })

        # Persist to SQLite — always, this is just a log
        session = next(get_session())
        run = Run(
            task=final_state["task"],
            final_output=final_state["final_output"],
            iterations=final_state["iteration"],
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        session.close()

        # Persist to ChromaDB — only if search actually succeeded
        if final_state.get("search_succeeded"):
            add_memory(
                run_id=run.id,
                task=final_state["task"],
                final_output=final_state["final_output"],
            )
        else:
            print(f"[SAFEGUARD] Skipped writing to long-term memory — search failed for task: {final_state['task']}")

        await websocket.send_json({
            "type": "done",
            "final_output": final_state["final_output"],
            "iterations": final_state["iteration"],
        })

    except WebSocketDisconnect:
        pass