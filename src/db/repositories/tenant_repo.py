from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict
import uuid
from passlib.context import CryptContext
from typing import Dict
from ..models import Tenant


pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TenantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_tenant(self, tenant_id: str, name: str) -> Dict:
        key = f"{tenant_id}.{uuid.uuid4()}"
        key_hash = pwd_hasher.hash(key)
        new_tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            api_key=key_hash)

        self.session.add(new_tenant)
        await self.session.commit()
        return {"api_key": key}

    async def get_tenant_id(self, name: str, api_key: str) -> Tenant | None:
        tenant = api_key.split(".")
        tenant = await self.session.execute(
            select(Tenant)
            .where(Tenant.id == tenant[0], Tenant.name == name))
        
        if tenant and pwd_hasher.verify(api_key, tenant.api_key):
            return tenant
        
        return None
