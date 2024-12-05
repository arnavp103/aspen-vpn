import argparse
from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="Aspen VPN Server - Coordinator",
    description="Serves as the Central Authority for the Aspen VPN",
    version="0.1.0",
    middleware=[],
)


# Join the network initially
# -- Registers their current network location
# -- If successful, receive network configuration updates.
@app.get("/connect")
def connect():
    return {"status": "connected"}

# Broadcast their presence to the network
@app.get("/broadcast-presence")
def broadcast_presence():
    return {"status": "broadcasted"}

# Get information about the peers they want to connect to
@app.get("/{peer_id}")
def read_peer(peer_id: int, query: str = None):
    return {"peer_id": peer_id}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aspen VPN Server")
    uvicorn.run(
        app="main:app",
        # host=...,
        # port=...,
        reload=True if not os.environ.get("production") else False,
        workers=1,
    )