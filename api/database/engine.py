from redis import Redis
from settings import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession


sync_engine = create_engine(settings.DATABASE_URL, echo=False)


def init_sync_db():
    SQLModel.metadata.create_all(bind=sync_engine)


def get_sync_db():
    with Session(sync_engine) as session:
        yield session


async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
    pool_recycle=1800,
)

async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_db():
    async with AsyncSession(async_engine) as session:
        yield session

def get_redis():
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0
    )
    try:
        yield client
    finally:
        client.close()
