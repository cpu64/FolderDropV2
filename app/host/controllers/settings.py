import os
from PyQt6.QtWidgets import QFileDialog
from app.models.settings import settings_store, Settings
from app.host.ui.settings import SettingsWindow


class SettingsWindowController:
    def __init__(self):
        self.settings_window = SettingsWindow(self.save_settings, self.browse_path)
        self.settings_window.setWindowTitle("Settings")
        self.settings_window.setMinimumSize(400, 300)
        self.settings_window.set_settings(settings_store.get_settings())
        self.settings_window.show()

    # ------------------------
    # Path browsing
    # ------------------------
    def browse_path(self, current_path):
        directory = QFileDialog.getExistingDirectory(
            self.settings_window,
            "Select Directory",
            current_path or "."
        )

        return directory if directory else current_path

    # ------------------------
    # Validation
    # ------------------------
    def validate_settings(self, data):
        try:
            port = int(data["port"])
        except ValueError:
            raise ValueError("Port must be a number")

        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")

        path = data["path"]

        if not os.path.exists(path):
            raise ValueError("Selected path does not exist")

        if not os.path.isdir(path):
            raise ValueError("Selected path is not a directory")

        if not os.access(path, os.R_OK):
            raise ValueError("No read permission for this directory")

        if not os.access(path, os.W_OK):
            raise ValueError("No write permission for this directory")

        return port, path

    # ------------------------
    # Save logic
    # ------------------------
    def save_settings(self, data):
        try:
            port, path = self.validate_settings(data)

            new_settings = Settings(
                password=data["password"],
                port=port,
                path=path,
                allow_upload=data["allow_upload"],
                allow_download=data["allow_download"],
                allow_rename=data["allow_rename"],
                allow_delete=data["allow_delete"],
            )

            settings_store.save_settings(new_settings)

            # Update settings_window state cleanly (no direct attribute access)
            self.settings_window.set_settings(new_settings, render=False)

        except ValueError as e:
            self.settings_window.show_error(str(e))
