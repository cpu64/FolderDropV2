import mimetypes
import os
from datetime import datetime

from app.host.interfaces.OwnerFileSystemInterface import OwnerFileSystemInterface
from app.models.FileSystemObject import FileSystemObject


class FileController:
    def __init__(self):
        self.owner_fs = OwnerFileSystemInterface()
        self.dir_cache = None
        self.root_path = ""

    def set_dir_cache(self, dir_cache, root_path):
        self.dir_cache = dir_cache
        self.root_path = root_path

    def _find_node(self, path):
        rel = os.path.relpath(path, self.root_path)
        if rel == ".":
            return self.dir_cache
        parts = rel.split(os.sep)
        return self.dir_cache.find_node(parts) if self.dir_cache else None

    def _find_parent_node(self, path):
        parent_path = os.path.dirname(path)
        return self._find_node(parent_path)

    def _update_ancestors(self, node):
        while node is not None and not node.is_root:
            node.update()
            node = node.parent_folder

    def on_deleted(self, event):
        node = self._find_node(event.src_path)
        if node is None:
            return
        node.delete()
        self._update_ancestors(node.parent_folder)

    def on_created(self, event):
        parent = self._find_parent_node(event.src_path)
        if parent is None:
            return
        name = os.path.basename(event.src_path)

        node = FileSystemObject.create_node(name=name, is_dir=event.is_directory)
        node.is_root = False

        if not event.is_directory:
            node.extension = name.rsplit(".", 1)[-1] if "." in name else ""
            mime, _ = mimetypes.guess_type(name)
            node.mime_type = mime or ""
            try:
                node.size = os.path.getsize(event.src_path)
            except OSError:
                node.size = 0

        node.create(parent)
        self._update_ancestors(parent)

    def on_modified(self, event):
        node = self._find_node(event.src_path)
        if node is None:
            return
        if not node.is_dir:
            try:
                node.size = os.path.getsize(event.src_path)
            except OSError:
                pass
        node.update()
        self._update_ancestors(node.parent_folder)

    def on_moved(self, event):
        node = self._find_node(event.src_path)
        if node is None:
            return
        old_parent = node.parent_folder
        node.delete()

        new_parent = self._find_parent_node(event.dest_path)
        if new_parent is None:
            return
        node.name = os.path.basename(event.dest_path)
        if not node.is_dir:
            node.extension = node.name.rsplit(".", 1)[-1] if "." in node.name else ""
            mime, _ = mimetypes.guess_type(node.name)
            node.mime_type = mime or ""
        node.create(new_parent)
        node.update()

        self._update_ancestors(new_parent)
        if old_parent is not new_parent:
            self._update_ancestors(old_parent)

    def checkFolderUsable(self, path):
        return self.owner_fs.checkFolderUsable(path)

    def getFolderContent(self, path):
        return self.owner_fs.getFolderContent(path)