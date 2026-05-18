import mimetypes
from datetime import datetime


class FileSystemObject:
    def __init__(self, name="", is_dir=False, size=0, created_at=None, modified_at=None):
        self.name = name
        self.created_at = created_at or datetime.now()
        self.modified_at = modified_at or datetime.now()
        self.size = size
        self.downloader_count = 0
        self.is_dir = is_dir
        self.extension = ""
        self.mime_type = ""
        self.is_root = False
        self.parent_folder = None

    @property
    def path(self):
        parts = []
        node = self
        while node and not node.is_root:
            parts.append(node.name)
            node = node.parent_folder
        return "/".join(reversed(parts))

    @property
    def url(self):
        if self.is_root:
            return "/"
        return f"/browse/{self.path}"

    def delete(self):
        if self.parent_folder is None:
            return
        if self.is_dir:
            self.parent_folder.child_folders = [
                c for c in self.parent_folder.child_folders if c is not self
            ]
        else:
            self.parent_folder.folders_file = [
                f for f in self.parent_folder.folders_file if f is not self
            ]
        self.parent_folder.element_count = (
                len(self.parent_folder.child_folders) + len(self.parent_folder.folders_file)
        )
        self.parent_folder._recalc_size()

    def create(self, parent):
        self.parent_folder = parent
        if self.is_dir:
            parent.child_folders.append(self)
        else:
            parent.folders_file.append(self)
        parent.element_count = len(parent.child_folders) + len(parent.folders_file)
        parent._recalc_size()

    def update(self):
        self.modified_at = datetime.now()

    def check_type(self):
        return "folder" if self.is_dir else "file"

    def increase_downloader_count(self):
        self.downloader_count += 1

    def decrease_downloader_count(self):
        if self.downloader_count > 0:
            self.downloader_count -= 1

    def __repr__(self):
        kind = "DIR" if self.is_dir else "FILE"
        return f"<FileSystemObject {kind} '{self.name}'>"

    @staticmethod
    def create_node(name="", is_dir=False, size=0, created_at=None, modified_at=None):
        if is_dir:
            from app.models.Folder import Folder
            return Folder(name=name, size=size, created_at=created_at, modified_at=modified_at)
        return FileSystemObject(name=name, is_dir=False, size=size, created_at=created_at, modified_at=modified_at)

