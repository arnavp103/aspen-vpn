import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout
import requests 


# Subclass QMainWindow to customize your application's main window
class GUI(QMainWindow):
    # Red or green server
    status = {
        "pending": "black",
        "online": "green",
        "offline": "red"
    }

    data = {}
    
    def __init__(self, address: str):
        super().__init__()

        self.setWindowTitle("Aspen VPN")

        layout = QVBoxLayout()

        self.status_circle = QLabel()
        self.status_circle.setFixedSize(8, 8)
        self.status_circle.setStyleSheet(f"background-color: {self.status['pending']}; border-radius: 4px;")

        server_status = QLabel("Server Status")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_circle)
        status_layout.addWidget(server_status)

        layout.addLayout(status_layout)

        peername_label = QLabel("Peer Name:")

        peername_input = QLineEdit()
        self.btn_connect = QPushButton("Connect to VPN")

        layout.addWidget(server_status)
        layout.addWidget(peername_label)
        layout.addWidget(peername_input)
        layout.addWidget(self.btn_connect)

        # Bind peername_input to data
        peername_input.textChanged.connect(lambda text: self.data.update({"peername": text}))

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def get_server_status(self, address: str):
        try:
            # Ping server to get status
            response = requests.get(address)
            if (response.status_code != 200):
                return self.status_circle.setStyleSheet(f"background-color: {self.status['offline']}; border-radius: 4px;")
        except requests.exceptions.ConnectionError:
            return self.status_circle.setStyleSheet(f"background-color: {self.status['offline']}; border-radius: 4px;")

        return self.status_circle.setStyleSheet(f"background-color: {self.status['online']}; border-radius: 4px;")

    @staticmethod
    async def setup(address: str, on_connect_click, on_disconnect_click):
        app = QApplication(sys.argv)
        window = GUI(address)
        window.get_server_status(address)
        
        window.btn_connect.clicked.connect((lambda _: on_connect_click(window.data)))

        window.show()

        app.exec()
        return app