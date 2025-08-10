from redis import Redis
from settings import settings
from sqlmodel import Session, SQLModel, create_engine


engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    """Create tables."""
    SQLModel.metadata.create_all(bind=engine)

def get_db():
    with Session(engine) as session:
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
        pass
