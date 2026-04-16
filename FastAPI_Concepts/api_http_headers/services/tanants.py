from uuid import UUID

from fastapi.params import Depends
from core.db import db_session
from models.tenants import Tenant
from schemas.tanents import TenantRequest, TenantResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class TenantService:
    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        self.session = session

    async def create_tenant(self, id: UUID, name: str):
        tenant_obj = Tenant(id=id, name=name)
        self.session.add(tenant_obj)
        await self.session.commit()
        await self.session.refresh(tenant_obj)
        tenant = {"id": tenant_obj.id, "name": tenant_obj.name}
        print(f"Tenant created: {tenant}")
        return tenant

    async def get_tenants(self):
        result = await self.session.execute(select(Tenant))
        tenants = result.scalars().all()
        return [{"id": t.id, "name": t.name} for t in tenants]
    