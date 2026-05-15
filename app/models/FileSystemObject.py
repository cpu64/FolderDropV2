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


class Folder(FileSystemObject):
    def __init__(self, name="", size=0, created_at=None, modified_at=None):
        super().__init__(
            name=name,
            is_dir=True,
            size=size,
            created_at=created_at,
            modified_at=modified_at,
        )
        self.child_folders = []
        self.folders_file = []
        self.element_count = 0

    def getFolderContents(self):
        return self.child_folders + self.folders_file

    def get_subfolders(self):
        return list(self.child_folders)

    def get_files(self):
        return list(self.folders_file)

    def find_node(self, relative_path_parts):
        if not relative_path_parts:
            return self
        target = relative_path_parts[0]
        rest = relative_path_parts[1:]
        for child in self.child_folders:
            if child.name == target:
                return child.find_node(rest)
        if not rest:
            for f in self.folders_file:
                if f.name == target:
                    return f
        return None

    def get_breadcrumbs(self):
        node_chain = []
        node = self
        while node:
            node_chain.append(node)
            if node.is_root:
                break
            node = node.parent_folder
        return [{"name": n.name, "url": n.url} for n in reversed(node_chain)]

    def get_parent_url(self):
        return self.parent_folder.url if self.parent_folder else None

    def update(self):
        self._recalc_size()
        self.element_count = len(self.child_folders) + len(self.folders_file)
        self.modified_at = datetime.now()

    def _recalc_size(self):
        self.size = sum(f.size for f in self.folders_file) + sum(c.size for c in self.child_folders)

    @classmethod
    def from_folder_content(cls, entries, parent_folder=None, is_root=False):
        folders = []
        files = []

        for entry in entries:
            if entry["is_dir"]:
                obj = cls(
                    name=entry["name"],
                    size=entry.get("size", 0),
                    created_at=datetime.fromtimestamp(entry["created_at"]) if entry.get("created_at") else None,
                    modified_at=datetime.fromtimestamp(entry["modified_at"]) if entry.get("modified_at") else None,
                )
                obj.parent_folder = parent_folder
                obj.is_root = is_root
                children = cls.from_folder_content(entry.get("children", []), parent_folder=obj)
                obj.child_folders = [c for c in children if c.is_dir]
                obj.folders_file = [c for c in children if not c.is_dir]
                obj.element_count = len(obj.child_folders) + len(obj.folders_file)
                folders.append(obj)
            else:
                obj = FileSystemObject(
                    name=entry["name"],
                    is_dir=False,
                    size=entry.get("size", 0),
                    created_at=datetime.fromtimestamp(entry["created_at"]) if entry.get("created_at") else None,
                    modified_at=datetime.fromtimestamp(entry["modified_at"]) if entry.get("modified_at") else None,
                )
                obj.parent_folder = parent_folder
                obj.extension = entry["name"].rsplit(".", 1)[-1] if "." in entry["name"] else ""
                mime, _ = mimetypes.guess_type(entry["name"])
                obj.mime_type = mime or ""
                files.append(obj)

        return folders + files

    def __repr__(self):
        return f"<Folder '{self.name}' ({self.element_count} items)>"
