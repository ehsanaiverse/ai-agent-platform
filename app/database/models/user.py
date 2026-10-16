from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.conversation import Conversation


class User(BaseModel):
    __tablename__ = "users"

    platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    platform_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    conversations: Mapped[list["Conversation"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
)