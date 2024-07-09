import models
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from logger import CustomFormatter
import logging



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

engine = False
#ИСПРАВИТЬ НА НОВОМ ПК
DB_LITE = "sqlite+aiosqlite:///W:/Pasman/Pasman/data/database"

try:
    engine = create_async_engine(url=DB_LITE)
    logger.info(f"engine успешно создан")
except Exception as e:
    logger.error(f"Произошла ошибка подключения к БД: {e}")

try:
    if engine:
        session_marker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        logger.info(f"session_marker успешно создан")
    else:
        raise TypeError('type(bind) = False а нужен <sqlalchemy.ext.asyncio.engine.AsyncEngine object at '
                        '0x000001CCF2636900>')
except Exception as e:
    logger.error(f"Произошла ошибка session_marker: {e}")


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)