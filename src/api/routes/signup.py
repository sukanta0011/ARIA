from fastapi import APIRouter, HTTPException, Depends, AsyncSession
from pydantic import Field
import uuid
from ...db.session import get_db
from ...db.repositories.tenant_repo import TenantRepository

router = APIRouter()

@router.post("/api_keys")
async def generate_api_key(
    name: str = Field(min_length=1, max_length=20),
    db: AsyncSession = Depends(get_db)):
    tenant_id = lambda: str(uuid.uuid4)
    tenant_repo = TenantRepository(db)

    api_key = await tenant_repo.register_tenant(tenant_id=tenant_id, name=name)

    return api_key
