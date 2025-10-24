from pydantic import BaseModel, Field
from typing import List, Optional

class Step(BaseModel):
    type: str
    source: Optional[str] = Field(default=None)
    symbol: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    to: Optional[str] = Field(default=None)

class WorkflowSchema(BaseModel):
    trigger: str
    steps: List[Step]
