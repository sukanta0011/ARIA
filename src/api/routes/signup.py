from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field
import uuid
from typing import Dict
from ...db.session import get_db
from ...db.repositories.tenant_repo import TenantRepository

router = APIRouter()


def validate_name(name: str) -> str | None:
    if len(name) > 50:
        return None
    return name


@router.post("/api_keys", response_model=None)
async def generate_api_key(
    name: str = Depends(validate_name),
    db: AsyncSession = Depends(get_db)) -> Dict:

    if not name:
        raise HTTPException(status_code=400, detail="User name should be below 50 character")

    tenant_id = str(uuid.uuid4())
    tenant_repo = TenantRepository(db)

    api_key = await tenant_repo.register_tenant(tenant_id=tenant_id, name=name)

    return {"api_key": api_key}
