import os

from quart import Quart, render_template, abort
from app.models.FileSystemObject import FileSystemObject, Folder
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio
import platform
import psutil


class WebController:
    def __init__(self, dir_cache):
        self.app = Quart(__name__, template_folder='../templates')
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
