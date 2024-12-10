"""CRUD operations for invites"""

from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..database.models import Invite
from ..schemas.invite import InviteCreate, InviteUpdate

def get_invite(db: Session, invite_id: int) -> Invite:
    """Get invite by ID"""
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    return invite

def get_invite_by_code(db: Session, code: str) -> Invite:
    """Get invite by code"""
    return db.query(Invite).filter(Invite.code == code).first()

def get_invites(db: Session, skip: int = 0, limit: int = 100) -> list[Invite]:
    """Get all invites"""
    return db.query(Invite).offset(skip).limit(limit).all()

def create_invite(db: Session, invite: InviteCreate) -> Invite:
    """Create new invite"""
    db_invite = Invite(
        code=Invite.generate_code(),
        expires_at=invite.expires_at,
        description=invite.description,
        used_by=invite.used_by,
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    return db_invite

def update_invite(db: Session, invite_id: int, invite_update: InviteUpdate) -> Invite:
    """Update invite information"""
    db_invite = get_invite(db, invite_id)
    update_data = invite_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_invite, field, value)

    db.commit()
    db.refresh(db_invite)
    return db_invite