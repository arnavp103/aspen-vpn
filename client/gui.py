import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aspen VPN")

        layout = QVBoxLayout()

        # Red or green server
        status = {
            "online": "green",
            "offline": "red"
        }
       
        server_status_value = status["offline"]
        self.status_circle = QLabel()
        self.status_circle.setFixedSize(8, 8)
        self.status_circle.setStyleSheet(f"background-color: {server_status_value}; border-radius: 4px;")

        server_status = QLabel("Server Status")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_circle)
        status_layout.addWidget(server_status)

        layout.addLayout(status_layout)

        peername_label = QLabel("Peer Name:")

        peername_input = QLineEdit()
        button = QPushButton("Connect to VPN")

        layout.addWidget(server_status)
        layout.addWidget(peername_label)
        layout.addWidget(peername_input)
        layout.addWidget(button)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
