"""Peer management routes"""

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List

from ..database.session import get_db
from ..database.models import Peer
from ..schemas.peer import PeerCreate, PeerInDB, PeerUpdate
from ..crud import peer as peer_crud
from ..services.ip_manager import IPManager
from ..wireguard import get_wg_server, sync_wireguard_peers

router = APIRouter()
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Initialize IP manager (move configuration to settings later)
ip_manager = IPManager("10.0.0.0/24", "10.0.0.1")


def verify_api_key(
    api_key: str = Security(API_KEY_HEADER), db: Session = Depends(get_db)
):
    """Verify API key belongs to an enabled peer"""
    peer = db.query(Peer).filter(Peer.api_key == api_key, Peer.is_enabled).first()
    if not peer:
        raise HTTPException(status_code=403, detail="Invalid or disabled API key")
    return peer


def verify_admin(
    api_key: str = Security(API_KEY_HEADER), db: Session = Depends(get_db)
):
    """Verify API key belongs to an admin peer"""
    peer = verify_api_key(api_key, db)
    if not peer.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return peer


@router.post("/register", response_model=PeerInDB)
async def register_peer(peer: PeerCreate, db: Session = Depends(get_db)):
    """Register a new peer"""
    if peer_crud.get_peer_by_name(db, peer.name):
        raise HTTPException(status_code=400, detail="Peer name already exists")

    # Create peer first to get ID
    db_peer = peer_crud.create_peer(db, peer)

    # Allocate IP address
    try:
        ip_address = ip_manager.allocate_ip(db, db_peer.id)
        print(f"[server]: Allocated IP {ip_address} to {peer.name}")
    except RuntimeError as e:
        peer_crud.delete_peer(db, db_peer.id)
        raise HTTPException(status_code=503, detail="No available IP addresses") from e

    # Add to WireGuard if successful
    wg_server = get_wg_server()
    sync_wireguard_peers(db, wg_server)

    return db_peer


@router.get("/", response_model=List[PeerInDB])
async def list_peers(
    current_peer: Peer = Depends(verify_api_key),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all peers"""
    return peer_crud.get_peers(db, skip=skip, limit=limit)


@router.get("/{peer_id}", response_model=PeerInDB)
async def get_peer(
    peer_id: int,
    current_peer: Peer = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get specific peer"""
    return peer_crud.get_peer(db, peer_id)


@router.put("/{peer_id}", response_model=PeerInDB)
async def update_peer(
    peer_id: int,
    peer_update: PeerUpdate,
    current_peer: Peer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Update peer information"""
    return peer_crud.update_peer(db, peer_id, peer_update)


@router.post("/{peer_id}/enable", response_model=PeerInDB)
async def enable_peer(
    peer_id: int, admin: Peer = Depends(verify_admin), db: Session = Depends(get_db)
):
    """Enable a peer"""
    peer = peer_crud.toggle_peer_status(db, peer_id, True)
    wg_server = get_wg_server()
    sync_wireguard_peers(db, wg_server)
    return peer


@router.post("/{peer_id}/disable", response_model=PeerInDB)
async def disable_peer(
    peer_id: int, admin: Peer = Depends(verify_admin), db: Session = Depends(get_db)
):
    """Disable a peer"""
    peer = peer_crud.toggle_peer_status(db, peer_id, False)
    wg_server = get_wg_server()
    sync_wireguard_peers(db, wg_server)
    return peer


@router.delete("/{peer_id}", response_model=PeerInDB)
async def delete_peer(
    peer_id: int, admin: Peer = Depends(verify_admin), db: Session = Depends(get_db)
):
    """Delete a peer and release their IP"""
    peer = peer_crud.get_peer(db, peer_id)
    if peer:
        ip_manager.release_ip(db, peer_id)
        peer_crud.delete_peer(db, peer_id)
    wg_server = get_wg_server()
    sync_wireguard_peers(db, wg_server)
    return peer
