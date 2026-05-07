from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict
import uuid
from passlib.context import CryptContext
from typing import Dict
import bcrypt
from ..models import Tenant


pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TenantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_tenant(self, tenant_id: str, name: str) -> Dict:
        key = str(uuid.uuid4())
        key_hash = pwd_hasher.hash(key)
        new_tenant = Tenant(
            id=tenant_id,
            name=name,
            api_key=key_hash)

        self.session.add(new_tenant)
        await self.session.commit()
        return {"api_key": f"{tenant_id}.{key}"}

    async def get_tenant_id(self, api_key: str) -> Tenant | None:
        tenant_id_keys = api_key.split(".")
        tenant_obj = await self.session.execute(
            select(Tenant)
            .where(Tenant.id==tenant_id_keys[0]))
        
        tenant = tenant_obj.scalars().first()
        if not tenant:
            return None

        if not pwd_hasher.verify(tenant_id_keys[1], tenant.api_key):
            return None
        
        return tenant
