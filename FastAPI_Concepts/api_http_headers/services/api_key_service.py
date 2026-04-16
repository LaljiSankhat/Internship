

from fastapi import Depends
from typing_extensions import Annotated
from uuid import UUID

from core.db import db_session
from models.api_keys import ApiKeys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class ApiKeyService:
    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        self.session = session  

    async def create_api_key(self, tenant_id: UUID, api: str):
        new_api_key = ApiKeys(tenant_id=tenant_id, api=api)
        self.session.add(new_api_key)
        await self.session.commit()
        await self.session.refresh(new_api_key)
        return new_api_key