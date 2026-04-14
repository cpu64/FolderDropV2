from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QWidget,
    QVBoxLayout
)

from app.host.ui.settings import SettingsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FolderDrop Main")

        self.settings_window = None

        # ------------------------
        # Central widget
        # ------------------------
        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout()
        container.setLayout(layout)

        # ------------------------
        # Buttons
        # ------------------------
        self.open_settings_btn = QPushButton("Open Settings")
        self.open_settings_btn.clicked.connect(self.open_settings)

        layout.addWidget(self.open_settings_btn)

    # ------------------------
    # Open settings window
    # ------------------------
    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWidget()

        self.settings_window.setWindowTitle("Settings")
        self.settings_window.setMinimumSize(400, 300)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
