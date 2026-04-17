import sys
from PyQt6.QtWidgets import QApplication

from app.host.ui.main import MainWindow
from app.host.controllers.settings import SettingsController

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self.open_settings)
        self.settings_controller = None

    def open_settings(self):
        # Create fresh instances each time (safe default)
        self.settings_controller = SettingsController()

    def run(self):
        self.main_window.show()
        return self.app.exec()
