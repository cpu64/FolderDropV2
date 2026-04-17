from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QPushButton, QMessageBox,
    QLabel, QLineEdit, QCheckBox,
    QHBoxLayout, QWidget
)


class SettingsWindow(QDialog):
    def __init__(self, save_settings, browse_path):
        super().__init__()

        self.save_settings = save_settings
        self.browse_path = browse_path

        self.settings = None
        self.edit_mode = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.button = QPushButton("Change Settings")
        self.button.clicked.connect(self.enter_edit_mode)
        self.layout.addWidget(self.button)

    # ------------------------
    # State setters
    # ------------------------
    def set_settings(self, settings, render=True):
        self.settings = settings
        if render:
            self.render()

    # ------------------------
    # Rendering
    # ------------------------
    def clear_form(self):
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

    def render(self):
        if not self.settings:
            return

        self.clear_form()

        # safely disconnect previous signal
        try:
            self.button.clicked.disconnect()
        except TypeError:
            pass

        if self.edit_mode:
            self.button.setText("Save Settings")
            self.button.clicked.connect(self.exit_edit_mode)
            self.render_edit_mode()
        else:
            self.button.setText("Change Settings")
            self.button.clicked.connect(self.enter_edit_mode)
            self.render_view_mode()

    # ------------------------
    # View mode
    # ------------------------
    def bool_label(self, value: bool):
        return QLabel("✅" if value else "❌")

    def render_view_mode(self):
        s = self.settings

        self.form_layout.addRow("Password:", QLabel("*" * len(s.password)))
        self.form_layout.addRow("Port:", QLabel(str(s.port)))
        self.form_layout.addRow("Path:", QLabel(s.path))
        self.form_layout.addRow("Allow Upload:", self.bool_label(s.allow_upload))
        self.form_layout.addRow("Allow Download:", self.bool_label(s.allow_download))
        self.form_layout.addRow("Allow Rename:", self.bool_label(s.allow_rename))
        self.form_layout.addRow("Allow Delete:", self.bool_label(s.allow_delete))

    # ------------------------
    # Edit mode
    # ------------------------
    def render_edit_mode(self):
        s = self.settings

        self.password_input = QLineEdit(s.password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.port_input = QLineEdit(str(s.port))

        # Path selector
        self.path_input = QLineEdit(s.path)
        self.path_input.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        path_widget = QWidget()
        path_widget.setLayout(path_layout)

        # Checkboxes
        self.allow_upload_input = QCheckBox()
        self.allow_upload_input.setChecked(s.allow_upload)

        self.allow_download_input = QCheckBox()
        self.allow_download_input.setChecked(s.allow_download)

        self.allow_rename_input = QCheckBox()
        self.allow_rename_input.setChecked(s.allow_rename)

        self.allow_delete_input = QCheckBox()
        self.allow_delete_input.setChecked(s.allow_delete)

        # Layout
        self.form_layout.addRow("Password:", self.password_input)
        self.form_layout.addRow("Port:", self.port_input)
        self.form_layout.addRow("Path:", path_widget)
        self.form_layout.addRow("Allow Upload:", self.allow_upload_input)
        self.form_layout.addRow("Allow Download:", self.allow_download_input)
        self.form_layout.addRow("Allow Rename:", self.allow_rename_input)
        self.form_layout.addRow("Allow Delete:", self.allow_delete_input)

    # ------------------------
    # Actions
    # ------------------------
    def enter_edit_mode(self):
        self.edit_mode = True
        self.render()

    def exit_edit_mode(self):
        data = self.collect_inputs()
        self.save_settings(data)
        self.edit_mode = False
        self.render()

    def collect_inputs(self):
        return {
            "password": self.password_input.text(),
            "port": self.port_input.text(),
            "path": self.path_input.text(),
            "allow_upload": self.allow_upload_input.isChecked(),
            "allow_download": self.allow_download_input.isChecked(),
            "allow_rename": self.allow_rename_input.isChecked(),
            "allow_delete": self.allow_delete_input.isChecked(),
        }

    def select_path(self):
        self.path_input.setText(self.browse_path(self.path_input.text()))

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
