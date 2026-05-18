from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout,
    QLabel, QMessageBox,
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, on_open_settings, on_start_sharing):
        super().__init__()

        # 56.1 nematau controller atributo
        self.setWindowTitle("FolderDrop Main")
        self.setMinimumSize(400, 250)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        self.open_settings_btn = QPushButton("Open Settings")
        self.open_settings_btn.clicked.connect(on_open_settings)
        layout.addWidget(self.open_settings_btn)

        self.start_sharing_btn = QPushButton("Start Sharing")
        self.start_sharing_btn.clicked.connect(on_start_sharing)
        layout.addWidget(self.start_sharing_btn)

        self.status_label = QLabel("Not sharing")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_link(self, link):
        self.status_label.setText(f"Sharing at: <a href='{link}'>{link}</a>")
        self.status_label.setOpenExternalLinks(True)
        self.start_sharing_btn.setEnabled(False)
        self.start_sharing_btn.setText("Sharing…")

    def forceStopSharing(self):
        pass

    def cancelStopSharing(self):
        pass

    def startSharing(self):
        pass

    def open_settings_btn_clicked(self):
        pass
