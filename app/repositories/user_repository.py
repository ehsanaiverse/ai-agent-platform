from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository responsible for all User database operations.
    """

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_platform_user_id(
        self,
        platform: str,
        platform_user_id: str,
    ) -> User | None:
        """
        Retrieve a user by messaging platform and platform user ID.
        """
        stmt = select(User).where(
            User.platform == platform,
            User.platform_user_id == platform_user_id,
        )

        return self.db.scalar(stmt)