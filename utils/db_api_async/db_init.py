from .db_api import async_engine
from .models import Base
from loguru import logger


# Асинхронная инициализация базы данных
async def init_db():
    async with async_engine.begin() as conn:
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
