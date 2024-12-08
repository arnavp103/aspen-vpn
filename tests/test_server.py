"""
A test application to see if the server or client are connected.

"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = f"Hello from {socket.gethostname()}! You connected from {self.client_address[0]}"
        self.wfile.write(response.encode())


def run_server(port=8080):
    server = HTTPServer(("10.0.0.1", port), SimpleHandler)  # Bind to VPN IP
    print(f"Starting server on VPN IP (10.0.0.1:{port})...")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
