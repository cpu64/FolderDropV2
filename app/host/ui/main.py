from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout


class MainWindow(QMainWindow):
    def __init__(self, open_settings):
        super().__init__()

        self.setWindowTitle("FolderDrop Main")

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        self.open_settings_btn = QPushButton("Open Settings")
        self.open_settings_btn.clicked.connect(open_settings)

        layout.addWidget(self.open_settings_btn)
