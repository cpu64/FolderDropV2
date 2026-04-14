from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QCheckBox, QFormLayout, QFileDialog, QHBoxLayout, QMessageBox
)
from app.host.controllers.settings import SettingsController
from app.models.settings import Settings
import os


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(self.windowFlags())

        self.controller = SettingsController()
        self.edit_mode = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.button = QPushButton("Change Settings")
        self.button.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.button)

        self.load_settings()

    # ------------------------
    # Load + Render
    # ------------------------
    def load_settings(self):
        self.settings = self.controller.get_settings()
        self.render()

    def clear_form(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

    def render(self):
        self.clear_form()

        if not self.edit_mode:
            self.render_view_mode()
            self.button.setText("Change Settings")
        else:
            self.render_edit_mode()
            self.button.setText("Save Settings")

    # ------------------------
    # Helpers
    # ------------------------
    def bool_label(self, value: bool) -> QLabel:
        return QLabel("✅" if value else "❌")

    def validate_inputs(self):
        # ------------------------
        # Validate port
        # ------------------------
        try:
            port = int(self.port_input.text())
        except ValueError:
            raise ValueError("Port must be a number")

        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")

        # ------------------------
        # Validate path
        # ------------------------
        path = self.path_input.text()

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
    # View Mode
    # ------------------------
    def render_view_mode(self):
        s = self.settings

        self.form_layout.addRow("Password:", QLabel("*" * len(s.password)))
        self.form_layout.addRow("Port:", QLabel(str(s.port)))
        self.form_layout.addRow("Path:", QLabel(s.path))
        self.form_layout.addRow("Allow Upload:", self.bool_label(s.allow_upload))
        self.form_layout.addRow("Allow Download:", self.bool_label(s.allow_download))
        self.form_layout.addRow("Allow Rename:", self.bool_label(s.allow_rename))
        self.form_layout.addRow("Allow Delete:", self.bool_label(s.allow_delete))

    def select_path(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.path_input.text() or "."
        )

        if directory:
            self.path_input.setText(directory)

    # ------------------------
    # Edit Mode
    # ------------------------
    def render_edit_mode(self):
        s = self.settings

        self.password_input = QLineEdit(s.password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.port_input = QLineEdit(str(s.port))

        # ------------------------
        # Path selector
        # ------------------------
        self.path_input = QLineEdit(s.path)
        self.path_input.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        # Wrap layout into a QWidget (required for QFormLayout)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)

        # ------------------------
        # Checkboxes
        # ------------------------
        self.allow_upload_input = QCheckBox()
        self.allow_upload_input.setChecked(s.allow_upload)

        self.allow_download_input = QCheckBox()
        self.allow_download_input.setChecked(s.allow_download)

        self.allow_rename_input = QCheckBox()
        self.allow_rename_input.setChecked(s.allow_rename)

        self.allow_delete_input = QCheckBox()
        self.allow_delete_input.setChecked(s.allow_delete)

        # ------------------------
        # Form layout
        # ------------------------
        self.form_layout.addRow("Password:", self.password_input)
        self.form_layout.addRow("Port:", self.port_input)
        self.form_layout.addRow("Path:", path_widget)
        self.form_layout.addRow("Allow Upload:", self.allow_upload_input)
        self.form_layout.addRow("Allow Download:", self.allow_download_input)
        self.form_layout.addRow("Allow Rename:", self.allow_rename_input)
        self.form_layout.addRow("Allow Delete:", self.allow_delete_input)

    # ------------------------
    # Toggle / Save
    # ------------------------
    def toggle_mode(self):
        if self.edit_mode:
            success = self.save_settings()
            if not success:
                return  # stay in edit mode if validation fails

        self.edit_mode = not self.edit_mode
        self.render()

    def save_settings(self):
        try:
            port, path = self.validate_inputs()

            new_settings = Settings(
                password=self.password_input.text(),
                port=port,
                path=path,
                allow_upload=self.allow_upload_input.isChecked(),
                allow_download=self.allow_download_input.isChecked(),
                allow_rename=self.allow_rename_input.isChecked(),
                allow_delete=self.allow_delete_input.isChecked(),
            )

            self.controller.update_settings(new_settings)
            self.settings = new_settings

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

        return True
