"""
A simple client to test if the vpn tunnel is working.
Must be used in conjunction with the test_server.py script.
"""

import requests


def test_vpn_connection():
    try:
        # Try to connect to the test server through VPN
        response = requests.get("http://10.0.0.1:8080")
        print(f"Response from VPN server: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting: {e}")


if __name__ == "__main__":
    test_vpn_connection()
