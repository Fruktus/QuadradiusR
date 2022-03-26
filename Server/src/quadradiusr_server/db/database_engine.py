from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from quadradiusr_server.config import DatabaseConfig


class DatabaseEngine:
    def __init__(self, config: DatabaseConfig) -> None:
        self.config: DatabaseConfig = config
        self.engine: AsyncEngine = create_async_engine(
            config.url,
            echo=config.log_statements,
            echo_pool=config.log_connections,
            hide_parameters=config.hide_parameters,
            pool_recycle=config.pool_recycle_timeout,
        )

    async def create_metadata(self):
        from quadradiusr_server.db.base import Base
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def initialize(self):
        if self.config.create_metadata:
            await self.create_metadata()

    async def dispose(self):
        await self.engine.dispose()

    def connect(self) -> AsyncConnection:
        return self.engine.connect()
