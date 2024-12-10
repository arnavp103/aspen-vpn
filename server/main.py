"""
Command line tool to spin up FastAPI server to handle VPN requests
"""

import argparse
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from python_wireguard import Server, Key
from pydantic import BaseModel


from .database.session import DatabaseSession, Base
from .routes import peers
from services.ip_manager import IPManager

# Initialize database singleton
db = DatabaseSession()
with db.get_session() as session:
    Base.metadata.create_all(bind=db.engine)


# Initialize IP manager
ip_manager = IPManager("10.0.0.0/24", "10.0.0.1")
with db.get_session() as session:
    ip_manager.initialize_ip_pool(session)


wg_server = None  # WireGuard server instance
server_public_key = None  # Store public key separately
endpoint = "127.0.0.1"  # Default endpoint upon which server is accessible


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    wg_server.delete_interface()


app = FastAPI(title="Aspen VPN Server", lifespan=lifespan)

# Include peer routes
app.include_router(peers.router, prefix="/api/peers", tags=["peers"])


class ServerInfo(BaseModel):
    """Server information sent to peers"""

    public_key: str
    endpoint: str
    port: int
    network_cidr: str


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
