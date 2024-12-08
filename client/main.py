"""
Command line tool to connect to Aspen VPN server
"""

import argparse
import requests
from python_wireguard import Client, Key, ServerConnection


def connect_to_vpn(server_url: str):
    """Connect to VPN server"""
    # Get server info
    server_info = requests.get(f"{server_url}/api/server-info").json()

    # Generate our keys
    private, public = Key.key_pair()

    # Register with server
    peer_info = {
        "name": "test-client",
        "public_key": str(public),
        "assigned_ip": "10.0.0.2/24",  # Hardcoded for now
    }

    response = requests.post(f"{server_url}/api/peers/register", json=peer_info)
    if response.status_code != 200:
        raise Exception(f"Failed to register: {response.json()}")

    # Create WireGuard client interface
    client = Client(interface_name="wg0", key=private, local_ip="10.0.0.2/24")

    # Create server connection
    server_conn = ServerConnection(
        Key(server_info["public_key"]), server_info["endpoint"], server_info["port"]
    )

    client.set_server(server_conn)
    client.connect()

    print("Connected to VPN!")
    print("Server public key:", server_info["public_key"])
    print("Your public key:", str(public))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aspen VPN Client")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    args = parser.parse_args()

    connect_to_vpn(args.server)
