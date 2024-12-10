"""CRUD operations for peers"""

from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..database.models import Peer
from ..schemas.peer import PeerCreate, PeerUpdate


def get_peer(db: Session, peer_id: int) -> Peer:
    """Get peer by ID"""
    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    return peer


def get_peer_by_name(db: Session, name: str) -> Peer:
    """Get peer by name"""
    return db.query(Peer).filter(Peer.name == name).first()


def get_peers(db: Session, skip: int = 0, limit: int = 100) -> list[Peer]:
    """Get all peers"""
    return db.query(Peer).offset(skip).limit(limit).all()


def create_peer(db: Session, peer: PeerCreate) -> Peer:
    """Create new peer"""
    db_peer = Peer(
        name=peer.name,
        public_key=peer.public_key,
        assigned_ip=peer.assigned_ip,
        api_key=Peer.generate_api_key(),
        description=peer.description,
    )
    db.add(db_peer)
    db.commit()
    db.refresh(db_peer)
    return db_peer


def update_peer(db: Session, peer_id: int, peer_update: PeerUpdate) -> Peer:
    """Update peer information"""
    db_peer = get_peer(db, peer_id)
    update_data = peer_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_peer, field, value)

    db.commit()
    db.refresh(db_peer)
    return db_peer


def toggle_peer_status(db: Session, peer_id: int, enable: bool) -> Peer:
    """Enable or disable a peer"""
    peer = get_peer(db, peer_id)
    peer.is_enabled = enable
    if enable:
        peer.last_seen = datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(peer)
    return peer
