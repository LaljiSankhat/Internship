from pydantic import BaseModel
from uuid import UUID

class TenantRequest(BaseModel):
    id: UUID
    name: str


class TenantResponse(BaseModel):
    id: UUID
    name: str