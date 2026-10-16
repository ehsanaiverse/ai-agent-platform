import structlog
from langgraph.checkpoint.memory import InMemorySaver
from app.core.config import settings

logger = structlog.get_logger(__name__)

"""
Central factory for the application's LangGraph checkpointer.

Supports persistent storage (PostgreSQL/Redis) for production horizontal scaling,
with seamless fallback to InMemorySaver.
"""


def create_checkpointer():
    if settings.CHECKPOINTER_TYPE.lower() == "postgres":
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            # Note: PostgresSaver requires standard connection string or pool
            saver = PostgresSaver.from_conn_string(settings.DATABASE_URL)
            logger.info("Initialized PostgreSQL persistent checkpointer for LangGraph")
            return saver
        except Exception as exc:
            logger.warning(
                "Failed to initialize PostgresSaver, falling back to InMemorySaver",
                error=str(exc),
            )

    return InMemorySaver()


checkpointer = create_checkpointer()