from datetime import datetime


class FileSystemObject:
    def __init__(self, name="", is_dir=False, size=0, created_at=None, modified_at=None):
        self.name = name
        self.is_dir = is_dir
        self.created_at = created_at or datetime.now()
        self.modified_at = modified_at or datetime.now()
        self.size = size
        self.downloader_count = 0
        self.children = []

    @classmethod
    def from_folder_content(cls, entries):
        objects = []
        for entry in entries:
            obj = cls(
                name=entry["name"],
                is_dir=entry["is_dir"],
                size=entry.get("size", 0),
                created_at=datetime.fromtimestamp(entry["created_at"]) if entry.get("created_at") else None,
                modified_at=datetime.fromtimestamp(entry["modified_at"]) if entry.get("modified_at") else None,
            )
            objects.append(obj)
        return objects

    def delete(self):
        pass

    def create(self):
        pass

    def update(self):
        pass

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
