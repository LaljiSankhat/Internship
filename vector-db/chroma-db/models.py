from pydantic import BaseModel
from typing import List



class UpsertRequest(BaseModel):
    documents: List[str]
    ids: List[str]


class QueryRequest(BaseModel):
    query_texts: List[str]
    n_results: int = 1
