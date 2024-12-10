"""WireGuard server management"""

from typing import Optional
from sqlalchemy.orm import Session
from python_wireguard import Server, ClientConnection, Key
from .database.models import Peer, IPAllocation

_wg_server: Optional[Server] = None


def get_wg_server() -> Server:
    """Get WireGuard server instance"""
    global _wg_server
    if not _wg_server:
        raise RuntimeError("WireGuard server not initialized")
    return _wg_server


def set_wg_server(server: Server) -> None:
    """Set WireGuard server instance"""
    global _wg_server
    _wg_server = server


def sync_wireguard_peers(db: Session, wg_server: Server) -> None:
    """Sync WireGuard peers with database state"""
    # Remove all current peers
    wg_server.delete_interface()
    wg_server.create_interface()
    wg_server.enable()

    # Add only enabled peers
    enabled_peers = db.query(Peer).filter(Peer.is_enabled).all()
    for peer in enabled_peers:
        ip = db.query(IPAllocation).filter(IPAllocation.peer_id == peer.id).first()
        if ip:
            client = ClientConnection(Key(peer.public_key), ip.ip_address)
            wg_server.add_client(client)
