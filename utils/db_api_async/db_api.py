from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

# Исправляем строку подключения для MySQL


# Создаем асинхронный движок
async_engine = create_async_engine(
    'sqlite+aiosqlite:///./files/wallets.db',
    echo=False,  # Можно включить для дебага
)

# Создаем фабрику для асинхронных сессий
async_session = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class Session:
    def __init__(self):
        self.session = async_session()

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            return e
        finally:
            await self.session.close()
