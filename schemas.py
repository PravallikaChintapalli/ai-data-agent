from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    question: str
    table_name: Optional[str] = None
