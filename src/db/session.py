from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from ..core.config import settings


engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(bind=engine)


async def get_db():
    async with async_session() as session:
        yield session
