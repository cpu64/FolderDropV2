import asyncio
import os
import platform
import psutil
from urllib.parse import unquote
from hypercorn.asyncio import serve
from hypercorn.config import Config
from quart import Quart, render_template, abort, jsonify, request

from app.host.interfaces.OwnerFileSystemInterface import OwnerFileSystemInterface
from app.models.settings import settings_store
from app.web.Interfaces.BrowserInterface import BrowserInterface
from app.models.FileSystemObject import FileSystemObject, Folder


class WebController:
    def __init__(self, dir_cache):
        self.app = Quart(__name__, template_folder='../templates')
        self.owner_file_system_interface = OwnerFileSystemInterface()
        self.browser_interface = BrowserInterface()
        self.dir_cache = dir_cache

        self.os_name = platform.system()
        path = settings_store.get_settings().path or "."
        best_match = ""
        self.fs_type = "unknown"
        for partition in psutil.disk_partitions(all=True):
            if path.startswith(partition.mountpoint):
                if len(partition.mountpoint) > len(best_match):
                    best_match = partition.mountpoint
                    self.fs_type = partition.fstype

        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        async def index():
            return await render_template(
                "index.html",
                folder=self.dir_cache,
                breadcrumbs=self.dir_cache.get_breadcrumbs(),
                parent_url=self.dir_cache.get_parent_url(),
                os_name=self.os_name,
                fs_type=self.fs_type.upper(),
            )

        @self.app.route("/browse/<path:subpath>")
        async def browse(subpath):
            parts = [p for p in subpath.split("/") if p]
            node = self.dir_cache.find_node(parts)
            if node is None or not node.is_dir:
                abort(404)
            return await render_template(
                "index.html",
                folder=node,
                breadcrumbs=node.get_breadcrumbs(),
                parent_url=node.get_parent_url(),
                os_name=self.os_name,
                fs_type=self.fs_type.upper(),
            )

        @self.app.route("/api/top-menu")
        async def top_menu():
            return await self.open_top_menu()

        @self.app.route("/upload_file")
        async def upload_file():
            settings = settings_store.get_settings()
            return jsonify({ "allow_upload": settings.allow_upload })

        @self.app.route("/api/menu")
        async def menu():
            return await self.open_menu()

        @self.app.route("/api/create-folder", methods=["POST"])
        async def create_folder_route():
            body = await request.get_json(silent=True) or {}
            current_path = unquote(body.get("current_path", "").strip())
            return await self.create_folder(current_path)

        @self.app.route("/api/download")
        async def download_route():
            rel_path = unquote(request.args.get("path", "").strip())
            return await self.download(rel_path)

    async def showFolder(self, folder: Folder):
        os_name = platform.system()

    async def open_top_menu(self):
        allow = settings_store.get_settings().allow_upload
        return jsonify({"allow_folder_creation": allow})

    async def open_menu(self):
        allow = settings_store.get_settings().allow_download
        return jsonify({"allow_download": allow})

    async def download(self, rel_path: str):
        settings = settings_store.get_settings()

        if not settings.allow_download:
            return jsonify({"ok": False, "error": "Downloading is disabled."}), 403

        parts = [p for p in rel_path.split("/") if p]
        node = self.dir_cache.find_node(parts)
        if node is None:
            return jsonify({"ok": False, "error": "File not found."}), 404

        full_path = os.path.join(settings.path, node.path)

        try:
            if node.is_dir:
                download_path = self.owner_file_system_interface.archive_folder(full_path)
                download_name = node.name + ".zip"
                archive_to_delete = download_path
            else:
                download_path = full_path
                download_name = node.name
                archive_to_delete = None

            node.increase_downloader_count()

            if not os.path.isfile(download_path):
                return jsonify({"ok": False, "error": "File not found."}), 404

            response = await self.browser_interface.download(download_path, download_name)
            original_stream = response.response

            class CleanupBodyWrapper:
                def __init__(self, stream):
                    self.stream = stream

                async def __aenter__(self):
                    if hasattr(self.stream, "__aenter__"):
                        await self.stream.__aenter__()
                    return self

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    try:
                        if hasattr(self.stream, "__aexit__"):
                            await self.stream.__aexit__(exc_type, exc_val, exc_tb)
                    finally:
                        node.decrease_downloader_count()
                        if archive_to_delete and os.path.isfile(archive_to_delete):
                            try:
                                os.remove(archive_to_delete)
                                tmp_dir = os.path.dirname(archive_to_delete)
                                if not os.listdir(tmp_dir):
                                    os.rmdir(tmp_dir)
                            except OSError:
                                pass

                async def __aiter__(self):
                    async for chunk in self.stream:
                        yield chunk

            response.response = CleanupBodyWrapper(original_stream)

            return response

        except FileNotFoundError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 404
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

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
