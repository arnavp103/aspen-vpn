"""
Command line tool to connect to Aspen VPN server
"""

import argparse
import requests
import asyncio
from python_wireguard import Client, Key, ServerConnection
from gui import GUI
import subprocess

interface_name = "wg1"
def connect_to_vpn(server_url: str):
    """Connect to VPN server"""
    # Get server info
    server_info = requests.get(f"{server_url}/api/server-info").json()
    print(f"[client]: server_info: {server_info}")

    # Generate our keys
    private, public = Key.key_pair()

    # Register with server
    peer_info = {
        "name": "test-client",
        "public_key": str(public),
        "assigned_ip": "10.0.0.2/24",  # Hardcoded for now
    }
    print(f"[client]: peer_info: {peer_info}")

    response = requests.post(f"{server_url}/api/peers/register", json=peer_info)
    if response.status_code != 200:
        raise Exception(f"Failed to register: {response.json()}")
    print("Registered with server!", response.json())

    interface_name = "wg1"
    # Create WireGuard client interface
    client = Client(interface_name=interface_name, key=private, local_ip="10.0.0.2/24")

    # Create server connection
    server_conn = ServerConnection(
        Key(server_info["public_key"]), server_info["endpoint"], server_info["port"]
    )

    client.set_server(server_conn)
    client.connect()
    
    print("Your public key:", str(public))
    # Bring up the WireGuard interface
    subprocess.run(["sudo", "ip", "link", "set", interface_name, "up"], check=True)

    # Add a default route through the VPN
    subprocess.run(["sudo", "ip", "route", "add", "default", "dev", interface_name], check=True)

    print("Connected to Aspen VPN!")
    print("Server public key:", server_info["public_key"])


def begin_connect(data):
    print("Connecting to VPN...")
    print(data)
    connect_to_vpn()
    pass

def begin_disconnect():
    print("Disconnecting from VPN...")
    pass

async def execute(args):
    """
    Initialize a GUI and connect to the VPN server.
    Determine if we have an existing interface or need to create a new one.
    """
    # app = await GUI.setup(args.server, begin_connect, begin_disconnect)

    # exit(1)
    # Check if we have an existing interface
    interfaces = subprocess.run(["ip", "link", "show"], capture_output=True, text=True).stdout

    if interface_name in interfaces:
        print(f"Interface {interface_name} already exists")
        # Check if the interface is up
        if "UP" in interfaces:
            print(f"Interface {interface_name} is up")
            # Check if the interface has an IP address
            if "inet" in interfaces:
                print(f"Interface {interface_name} has an IP address")
                # Check if the interface has a default route
                if "default" in interfaces:
                    print(f"Interface {interface_name} has a default route")
                else:
                    print(f"Interface {interface_name} does not have a default route")
            else:
                print(f"Interface {interface_name} does not have an IP address")
        else:
            print(f"Interface {interface_name} is not up")
    else:
        print(f"Interface {interface_name} does not exist")


    connect_to_vpn(args.server) 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Aspen VPN Client")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    args = parser.parse_args()

    asyncio.run(execute(args))