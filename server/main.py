"""
Command line tool to spin up FastAPI server to handle VPN requests
"""

import argparse
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security
from python_wireguard import Server, Key, ClientConnection
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import APIKeyHeader

from .database.session import DatabaseSession, get_db, Base
from .database import models
from .schemas.peer import PeerCreate, PeerInDB
from .crud import peer as peer_crud
from .database.models import Peer

# Initialize database singleton
db = DatabaseSession()
with db.get_session() as session:
    Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="Aspen VPN Server")

wg_server = None  # WireGuard server instance
server_public_key = None  # Store public key separately
endpoint = "127.0.0.1"  # Default endpoint upon which server is accessible

# Security header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")


def verify_api_key(
    api_key: str = Security(API_KEY_HEADER), db: Session = Depends(get_db)
):
    """Verify API key belongs to an enabled peer"""
    peer = (
        db.query(models.Peer).filter(Peer.api_key == api_key, Peer.is_enabled).first()
    )
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


def sync_wireguard_peers(db: Session):
    """Sync WireGuard peers with database state"""
    global wg_server
    # Remove all current peers
    wg_server.delete_interface()
    wg_server.create_interface()
    wg_server.enable()

    # Add only enabled peers
    enabled_peers = db.query(Peer).filter(Peer.is_enabled).all()
    for peer in enabled_peers:
        client = ClientConnection(
            Key(peer.public_key),
            peer.assigned_ip.split("/")[0],
        )
        wg_server.add_client(client)


class ServerInfo(BaseModel):
    """Server information sent to peers"""

    public_key: str
    endpoint: str
    port: int
    network_cidr: str


@asynccontextmanager
async def lifespan():
    """Initialize WireGuard interface on server start"""
    global wg_server, server_public_key

    # Generate server keys
    private, public = Key.key_pair()
    server_public_key = public  # Store public key

    print(f"Creating subnet 10.0.0.1/24 on {endpoint}")

    # Create WireGuard interface
    # Using 10.0.0.1/24 as our VPN subnet
    wg_server = Server(
        interface_name="wg0",
        key=private,
        local_ip="10.0.0.1/24",
        port=51820,
    )
    wg_server.enable()
    print("[server]: WireGuard server enabled")
    yield

    print("[server]: Cleaning up WireGuard server")
    # Remove interfaces
    wg_server.disable()
    wg_server.delete_interface()


@app.get("/api/server-info", response_model=ServerInfo)
async def get_server_info():
    """Return server connection information"""
    if not wg_server or not server_public_key:
        detail = f"Server not initialized - {'Missing WireGuard server' if not wg_server else ''} - {'Missing public key' if not server_public_key else ''}"
        raise HTTPException(status_code=500, detail=detail)

    return ServerInfo(
        public_key=str(server_public_key),
        endpoint=endpoint,
        port=51820,
        network_cidr="10.0.0.0/24",
    )


@app.post("/api/peers/register", response_model=PeerInDB)
async def register_peer(peer: PeerCreate, db: Session = Depends(get_db)):
    """Register a new peer with the server"""
    if peer_crud.get_peer_by_name(db, peer.name):
        raise HTTPException(status_code=400, detail="Peer name already exists")

    # Create peer in database first
    peer_dict = peer.model_dump()
    peer_dict["api_key"] = models.Peer.generate_api_key()
    # First peer is admin
    peer_count = db.query(models.Peer).count()
    peer_dict["is_admin"] = peer_count == 0

    db_peer = peer_crud.create_peer(db, PeerCreate(**peer_dict))

    # Add to WireGuard if successful
    client = ClientConnection(
        Key(peer.public_key),
        peer.assigned_ip.split("/")[0],
    )
    wg_server.add_client(client)

    return db_peer


@app.get("/api/peers", response_model=List[PeerInDB])
async def list_peers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all peers"""
    return peer_crud.get_peers(db, skip=skip, limit=limit)


@app.post("/api/peers/{peer_id}/enable", response_model=PeerInDB)
async def enable_peer(
    peer_id: int,
    admin: models.Peer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Enable a peer"""
    peer = peer_crud.toggle_peer_status(db, peer_id, True)
    sync_wireguard_peers(db)
    return peer


@app.post("/api/peers/{peer_id}/disable", response_model=PeerInDB)
async def disable_peer(
    peer_id: int,
    admin: models.Peer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Disable a peer"""
    peer = peer_crud.toggle_peer_status(db, peer_id, False)
    sync_wireguard_peers(db)
    return peer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aspen VPN Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument(
        "--endpoint",
        default="127.0.0.1",
        help="Ip address upon which the server is accessible",
    )
    args = parser.parse_args()
    endpoint = args.endpoint

    print("[server]: Starting VPN")
    uvicorn.run(app, host=args.host, port=args.port)
