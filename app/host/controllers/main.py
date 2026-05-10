import os
import sys
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt6.QtWidgets import QApplication

from app.host.ui.main import MainWindow
from app.host.controllers.settings import SettingsWindowController
from app.host.controllers.FileController import FileController
from app.models.settings import settings_store
from app.models.FileSystemObject import FileSystemObject


class MainWindowController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(
            on_open_settings=self.open_settings,
            on_start_sharing=self.startSharing,
        )
        self.settings_controller = None
        self.file_controller = FileController()
        self.dir_cache = None

    def open_settings(self):
        # Create fresh instances each time (safe default)
        self.settings_controller = SettingsWindowController()

    def run(self):
        self.main_window.show()
        return self.app.exec()

    def startSharing(self):
        settings = settings_store.get_settings()
        error = self.validateSettings(settings)
        if error:
            self.main_window.show_error(error)
            return

        try:
            folder_info = self.file_controller.checkFolderUsable(settings.path)
        except ValueError as e:
            self.main_window.show_error(str(e))
            return

        folder_content = self.file_controller.getFolderContent(settings.path)

        root = FileSystemObject(name=os.path.basename(settings.path), is_dir=True)
        root.is_root = True
        children = FileSystemObject.from_folder_content(folder_content, parent_folder=root)
        root.child_folders = [c for c in children if c.is_dir]
        root.folders_file = [c for c in children if not c.is_dir]
        root.element_count = len(root.child_folders) + len(root.folders_file)
        root._recalc_size()
        self.dir_cache = root

        self.file_controller.set_dir_cache(self.dir_cache, settings.path)

        try:
            self.activateSharing(settings)
        except Exception as e:
            self.main_window.show_error(f"Failed to start sharing: {e}")
            return

        self.file_controller.owner_fs.set_file_controller(self.file_controller)
        self.file_controller.owner_fs.start_watching(settings.path)

        link = self.generateLink(settings)
        self.main_window.show_link(link)

    def validateSettings(self, settings):
        if not settings.path:
            return "Shared folder path is not set."
        if not settings.port or settings.port < 1 or settings.port > 65535:
            return "Port must be between 1 and 65535."
        return None

    def activateSharing(self, settings):
        controller = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(handler):
                handler.send_response(200)
                handler.send_header("Content-Type", "text/plain; charset=utf-8")
                handler.end_headers()
                lines = []
                root = controller.dir_cache
                if root:
                    MainWindowController._render_tree(root, lines, indent=0)
                handler.wfile.write("\n".join(lines).encode("utf-8"))
                handler.wfile.write(b"\n")

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("0.0.0.0", settings.port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

    @staticmethod
    def _render_tree(obj, lines, indent=0):
        prefix = "  " * indent
        kind = "DIR" if obj.is_dir else "FILE"
        lines.append(f"{prefix}[{kind}] {obj.name}  ({obj.size} bytes)")
        for child in obj.child_folders:
            MainWindowController._render_tree(child, lines, indent + 1)
        for f in obj.folders_file:
            MainWindowController._render_tree(f, lines, indent + 1)

    def generateLink(self, settings=None):
        if settings is None:
            settings = settings_store.get_settings()
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip = "127.0.0.1"
        return f"http://{ip}:{settings.port}"

    def CanStop(self):
        pass

    def stopSharing(self):
        pass

    def forceStopSharing(self):
        pass
