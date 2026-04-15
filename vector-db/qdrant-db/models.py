from pydantic import BaseModel
from typing import List



class UpsertRequest(BaseModel):
    documents: List[str]
    ids: List[str]
