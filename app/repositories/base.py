from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common data-access operations.

    Transaction management is intentionally left to the service layer.
    """

    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def add(self, obj: ModelType) -> ModelType:
        """
        Add an object to the current transaction.
        """
        self.db.add(obj)
        return obj

    def get_by_id(self, obj_id: UUID) -> ModelType | None:
        """
        Retrieve an object by its primary key.
        """
        return self.db.get(self.model, obj_id)

    def delete(self, obj: ModelType) -> None:
        """
        Mark an object for deletion.
        """
        self.db.delete(obj)

    def flush(self) -> None:
        """
        Flush pending SQL statements to the database
        without committing the transaction.
        """
        self.db.flush()

    def refresh(self, obj: ModelType) -> None:
        """
        Reload an object's state from the database.
        """
        self.db.refresh(obj)