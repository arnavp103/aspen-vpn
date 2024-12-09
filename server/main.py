"""
Command line tool to spin up FastAPI server to handle VPN requests
"""

import argparse
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from python_wireguard import Server, Key, ClientConnection
from pydantic import BaseModel

app = FastAPI(title="Aspen VPN Server")

# In-memory storage for our prototype
peers = {}  # Dict to store peer info
wg_server = None  # WireGuard server instance
server_public_key = None  # Store public key separately


class PeerInfo(BaseModel):
    """Basic peer information"""

    name: str
    public_key: str
    assigned_ip: str


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

    # Create WireGuard interface
    # Using 10.0.0.1/24 as our VPN subnet
    wg_server = Server(
        interface_name="wg0",
        key=private,
        local_ip="10.0.0.1/24",  # Fixed: local_ip param instead of address
        port=51820,
    )
    wg_server.enable()
    yield
    # Remove interfaces
    wg_server.disable()

    
# @app.on_event("startup")
# async def startup_event():
#     """Initialize WireGuard interface on server start"""
#     global wg_server, server_public_key

#     # Generate server keys
#     private, public = Key.key_pair()
#     server_public_key = public  # Store public key

#     # Create WireGuard interface
#     # Using 10.0.0.1/24 as our VPN subnet
#     wg_server = Server(
#         interface_name="wg0",
#         key=private,
#         local_ip="10.0.0.1/24",  # Fixed: local_ip param instead of address
#         port=51820,
#     )
#     wg_server.enable()


@app.get("/api/server-info", response_model=ServerInfo)
async def get_server_info():
    """Return server connection information"""
    if not wg_server or not server_public_key:
        raise HTTPException(status_code=500, detail="Server not initialized")

    return ServerInfo(
        public_key=str(server_public_key),
        endpoint="192.168.2.113",  # Should be your server's public IP # Change this to localhost for local testing
        port=51820,
        network_cidr="10.0.0.0/24",
    )


@app.post("/api/peers/register")
async def register_peer(peer: PeerInfo):
    """Register a new peer with the server"""
    if peer.name in peers:
        raise HTTPException(status_code=400, detail="Peer name already exists")

    # Create WireGuard client connection
    client = ClientConnection(
        Key(peer.public_key),
        peer.assigned_ip.split("/")[0],  # Just use the IP without CIDR
    )
    print(f"[server]: client: {client.local_ip}")

    # Add to WireGuard interface
    wg_server.add_client(client)

    # Store peer info
    peers[peer.name] = peer

    return {"status": "registered"}


@app.get("/api/peers", response_model=List[PeerInfo])
async def list_peers():
    """List all connected peers"""
    return list(peers.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aspen VPN Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
