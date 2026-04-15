from pydantic import BaseModel
from typing import List

class UpsertRequest(BaseModel):
    documents: List[str]

class QueryRequest(BaseModel):
    query_text: str
    n_results: int = 5
