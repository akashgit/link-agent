import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.config import settings

_pool: AsyncConnectionPool | None = None
_saver: AsyncPostgresSaver | None = None


async def init_checkpointer() -> None:
    global _pool, _saver

    # Run setup with autocommit since it uses CREATE INDEX CONCURRENTLY
    async with await psycopg.AsyncConnection.connect(
        settings.checkpoint_database_url, autocommit=True
    ) as conn:
        saver = AsyncPostgresSaver(conn=conn)
        await saver.setup()

    # Now create the pool for ongoing use
    _pool = AsyncConnectionPool(
        conninfo=settings.checkpoint_database_url,
        open=False,
    )
    await _pool.open()
    _saver = AsyncPostgresSaver(conn=_pool)


async def get_checkpointer() -> AsyncPostgresSaver:
    if _saver is None:
        await init_checkpointer()
    assert _saver is not None
    return _saver


async def close_checkpointer() -> None:
    global _pool, _saver
    if _pool is not None:
        await _pool.close()
    _pool = None
    _saver = None
