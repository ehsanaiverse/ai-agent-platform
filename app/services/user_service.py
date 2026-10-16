from app.database.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """
    Business logic related to users.
    """
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_or_create_user(
        self,
        platform: str,
        platform_user_id: str,
        display_name: str,
    ) -> User:
        """
        Retrieve an existing user or create a new one.
        """

        user = self.repository.get_by_platform_user_id(
            platform=platform,
            platform_user_id=platform_user_id,
        )

        if user:
            if user.display_name != display_name:
                user.display_name = display_name

            return user

        user = User(
            platform=platform,
            platform_user_id=platform_user_id,
            display_name=display_name,
        )

        self.repository.add(user)
        self.repository.flush()
        self.repository.refresh(user)

        return user