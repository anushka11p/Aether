from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task: str
    final_output: Optional[str] = None
    iterations: int
    created_at: datetime = Field(default_factory=datetime.utcnow)