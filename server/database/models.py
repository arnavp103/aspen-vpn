"""SQLAlchemy models of the database"""

from datetime import datetime, timezone
import secrets
from typing import Optional
from sqlalchemy import Boolean, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # Relationship to IP allocation
    ip_allocation: Mapped["IPAllocation"] = relationship(
        back_populates="peer", uselist=False
    )

    @staticmethod
    def generate_api_key():
        """Generate a random API key"""
        return f"vpn_{secrets.token_urlsafe(32)}"

    def update_last_seen(self) -> None:
        """Update last seen timestamp"""
        self.last_seen = datetime.now(timezone.utc)


class IPAllocation(Base):
    """IP address allocation"""

    __tablename__ = "ip_allocations"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(String, unique=True, index=True)
    peer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("peers.id"), unique=True)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to peer
    peer: Mapped[Optional["Peer"]] = relationship(back_populates="ip_allocation")


class Invite(Base):
    """Invite model for database"""

    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    used_by: Mapped[Optional[int]] = mapped_column(ForeignKey("peers.id"), nullable=True)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    @staticmethod
    def generate_code() -> str:
        """Generate a random invite code"""
        return secrets.token_urlsafe(32)

    def is_expired(self) -> bool:
        """Check if invite is expired"""
        return self.expires_at is not None and self.expires_at < datetime.utcnow()

    def decrement_uses(self) -> None:
        """Decrement uses of invite"""
        self.max_uses -= 1