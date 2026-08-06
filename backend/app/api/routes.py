from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from app.agents.orchestrator import build_graph
from app.core.state import AgentState
from app.core.database import get_session
from app.models.run import Run

router = APIRouter()
graph = build_graph()

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    final_output: str
    iterations: int

@router.post("/run", response_model=TaskResponse)
def run_task(request: TaskRequest):
    initial_state: AgentState = {
        "task": request.task,
        "research_notes": None,
        "draft": None,
        "critique": None,
        "final_output": None,
        "iteration": 0,
        "next_agent": None,
        "search_succeeded": False,
    }
    result = graph.invoke(initial_state)
    return TaskResponse(
        final_output=result["final_output"],
        iterations=result["iteration"],
    )

@router.get("/history")
def get_history():
    session = next(get_session())
    runs = session.exec(select(Run).order_by(Run.created_at.desc())).all()
    session.close()
    return runs