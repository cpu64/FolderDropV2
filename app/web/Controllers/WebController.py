from urllib.parse import unquote
import os

from quart import Quart, render_template, abort, jsonify, request
from app.models.FileSystemObject import FileSystemObject, Folder
from app.models.settings import settings_store
from app.host.interfaces.OwnerFileSystemInterface import OwnerFileSystemInterface
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio
import platform
import psutil


class WebController:
    def __init__(self, dir_cache):
        self.app = Quart(__name__, template_folder='../templates')
        self.owner_file_system_interface = OwnerFileSystemInterface()
        self.dir_cache = dir_cache
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        async def index():
            return await self.showFolder(self.dir_cache)

        @self.app.route("/browse/<path:subpath>")
        async def browse(subpath):
            parts = [p for p in subpath.split("/") if p]
            node = self.dir_cache.find_node(parts)
            if node is None or not node.is_dir:
                abort(404)
            return await self.showFolder(node)

        @self.app.route("/api/top-menu")
        async def top_menu():
            return await self.open_top_menu()

        @self.app.route("/api/create-folder", methods=["POST"])
        async def create_folder_route():
            body = await request.get_json(silent=True) or {}
            current_path = unquote(body.get("current_path", "").strip())
            return await self.create_folder(current_path)

    async def showFolder(self, folder: Folder):
        os_name = platform.system()

        path = "."
        best_match = ""
        fs_type = "unknown"
        for partition in psutil.disk_partitions(all=True):
            if path.startswith(partition.mountpoint):
                if len(partition.mountpoint) > len(best_match):
                    best_match = partition.mountpoint
                    fs_type = partition.fstype

        return await render_template(
            "index.html",
            folder=folder,
            breadcrumbs=folder.get_breadcrumbs(),
            parent_url=folder.get_parent_url(),
            os_name=os_name,
            fs_type=fs_type.upper(),
        )

    async def open_top_menu(self):
        allow = settings_store.get_settings().allow_upload
        return jsonify({"allow_folder_creation": allow})

    async def create_folder(self, current_path: str):
        settings = settings_store.get_settings()

        if not settings.allow_upload:
            return jsonify({"ok": False, "error": "Folder creation is disabled."}), 403

        rel_path = os.path.join(current_path, "new_folder") if current_path else "new_folder"

        try:
            full_path = os.path.join(settings_store.get_settings().path, rel_path)
            self.owner_file_system_interface.mkdir(full_path)
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

        created = os.path.join(settings.path, rel_path)
        return jsonify({"ok": True, "path": created})

    def run(self, host="0.0.0.0", port=5000):
        config = Config()
        config.bind = [f"{host}:{port}"]

        async def start():
            await serve(
                self.app,
                config,
                shutdown_trigger=lambda: asyncio.Future()
            )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start())
