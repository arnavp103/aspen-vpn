"""Integration test for VPN server and client"""

import subprocess
import time
from contextlib import contextmanager
import requests
from python_wireguard import Key

SERVER_URL = "http://127.0.0.1:8000"
VPN_SERVER_IP = "10.0.0.1"


@contextmanager
def run_server():
    """Run the VPN server in a subprocess"""
    server_process = subprocess.Popen(
        ["python", "-m", "server.main", "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("Server PID:", server_process.pid)
    try:
        # Wait for server to start
        time.sleep(2)
        yield server_process
    finally:
        server_process.terminate()
        subprocess.run(["sudo", "./cleanup.sh"])


def test_vpn_connection():
    """Test complete VPN connection flow"""
    with run_server():
        # 1. Generate client keys
        private, public = Key.key_pair()

        # 2. Get server info
        server_info = requests.get(f"{SERVER_URL}/api/server-info").json()
        print(f"Server Info: {server_info}")

        # 3. Register peer
        peer_data = {
            "name": "test-client",
            "public_key": str(public),
            "assigned_ip": "10.0.0.2/24",
        }

        register_response = requests.post(
            f"{SERVER_URL}/api/peers/register", json=peer_data
        )
        print(f"Register Response: {register_response.json()}")
        api_key = register_response.json()["api_key"]

        # 4. Setup client WireGuard interface
        from python_wireguard import Client, ServerConnection

        client = Client(interface_name="wg1", key=private, local_ip="10.0.0.2/24")

        server_conn = ServerConnection(
            Key(server_info["public_key"]), server_info["endpoint"], server_info["port"]
        )

        client.set_server(server_conn)
        client.connect()

        # 5. Test VPN connectivity
        try:
            # Test ping
            ping_result = subprocess.run(
                ["ping", "-c", "1", VPN_SERVER_IP], capture_output=True, text=True
            )
            print("Ping test:", "Success" if ping_result.returncode == 0 else "Failed")
            print(ping_result.stdout)

            # List peers (requires API key)
            peers_response = requests.get(
                f"{SERVER_URL}/api/peers", headers={"X-API-Key": api_key}
            )
            print(f"Peers list: {peers_response.json()}")

            # Test disable/enable (requires admin)
            toggle_response = requests.post(
                f"{SERVER_URL}/api/peers/1/disable", headers={"X-API-Key": api_key}
            )
            print(f"Toggle response: {toggle_response.json()}")

        finally:
            client.disconnect()


if __name__ == "__main__":
    test_vpn_connection()
