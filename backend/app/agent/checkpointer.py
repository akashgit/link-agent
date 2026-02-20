from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings

_saver: AsyncPostgresSaver | None = None


async def get_checkpointer() -> AsyncPostgresSaver:
    global _saver
    if _saver is None:
        _saver = AsyncPostgresSaver.from_conn_string(settings.checkpoint_database_url)
        await _saver.setup()
    return _saver


async def close_checkpointer() -> None:
    global _saver
    if _saver is not None:
        _saver = None
