from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.session import get_db

def get_db_session() -> Generator[Session, None, None]:
    """
    API-level database dependency.

    This wraps the infrastructure database dependency so that
    API modules depend only on the API dependency layer.
    """
    yield from get_db()