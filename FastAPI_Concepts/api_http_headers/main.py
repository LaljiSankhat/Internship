from fastapi import Depends, FastAPI, HTTPException, Path, Request
from dotenv import load_dotenv
from fastapi.concurrency import asynccontextmanager
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api_key_service import ApiKeyService
from core.db import db_session
from models.api_keys import ApiKeys
from models.tenants import Tenant
from schemas.tanents import TenantRequest, TenantResponse
from uuid import UUID, uuid4
import secrets

from core.db import init_db
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Annotated
from services.tanants import TenantService
load_dotenv()  # Load environment variables from .env file


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        raise
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# @app.get("/generate_uuid")
# def generate_uuid():
#     new_uuid = str(uuid4())
#     return {"uuid": new_uuid}

@app.post("/create_tenant")
async def create_tenant(
    tenant: TenantRequest,
    service: Annotated[TenantService, Depends()]
):
    tenant_response = await service.create_tenant(id=uuid4(), name=tenant.name)
    return tenant_response

@app.get("/tenants")
async def get_tenants(
    service: Annotated[TenantService, Depends()]
):
    tenants = await service.get_tenants()
    return tenants


@app.post("/generate_api_key/{tenant_id}")
async def generate_api_key(
    service: Annotated[ApiKeyService, Depends()],
    tenant_id: UUID = Path(..., title="Tenant ID", description="The ID of the tenant"),
):
    tenant_result = await service.session.execute(
        select(Tenant.id).where(Tenant.id == tenant_id)
    )
    tenant_exists = tenant_result.scalar_one_or_none()
    if tenant_exists is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    generated_api_key = secrets.token_urlsafe(32)
    api_key = await service.create_api_key(tenant_id=tenant_id, api=generated_api_key)
    return {
        "id": str(api_key.id),
        "tenant_id": str(api_key.tenant_id),
        "api": api_key.api,
    }


@app.get("/access_info_with_api_headers/{tenant_id}")
async def access_info_with_headers(
    request: Request,
    tenant_id: UUID = Path(...,title="Tenant ID",description="The ID of the tenant"),
    x_api_key: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    session: Annotated[AsyncSession, Depends(db_session)] = None,
):
    if session is None:
        raise HTTPException(status_code=500, detail="Database session unavailable")

    result = await session.execute(
        select(ApiKeys).where(
            ApiKeys.tenant_id == tenant_id,
            ApiKeys.api == x_api_key.credentials,
        )
    )
    db_key = result.scalars().first()
    if not db_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return {
        "message": "Accessed info with API headers",
        "headers": {
            "id": str(db_key.id),
            "tenant_id": str(db_key.tenant_id),
        }
    }

# START THE SERVER WITH: uvicorn main:app --reload
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)