"""SQLAlchemy models of the database"""

from datetime import datetime, timezone
import secrets
from typing import Optional
from sqlalchemy import Boolean, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


class Peer(Base):
    """Peer model for database"""

    __tablename__ = "peers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True)
    public_key: Mapped[str] = mapped_column(String, unique=True)
    assigned_ip: Mapped[str] = mapped_column(String, unique=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # authentication info
    api_key: Mapped[str] = mapped_column(String, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    @staticmethod
    def generate_api_key():
        """Generate a random API key"""
        return f"vpn_{secrets.token_urlsafe(32)}"

    def update_last_seen(self) -> None:
        """Update last seen timestamp"""
        self.last_seen = datetime.now(timezone.utc)
