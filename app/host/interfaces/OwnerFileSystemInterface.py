import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.models.settings import settings_store


class OwnerFileSystemInterface(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_controller = None
        self._observer = None

    def set_file_controller(self, file_controller):
        self.file_controller = file_controller

    def start_watching(self, path):
        self._observer = Observer()
        self._observer.schedule(self, path, recursive=True)
        self._observer.start()

    def stop_watching(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def on_deleted(self, event):
        if self.file_controller:
            self.file_controller.on_deleted(event)

    def on_created(self, event):
        if self.file_controller:
            self.file_controller.on_created(event)

    def on_modified(self, event):
        if self.file_controller:
            self.file_controller.on_modified(event)

    def on_moved(self, event):
        if self.file_controller:
            self.file_controller.on_moved(event)

    def browse_folders(self):
        pass

    def mkdir(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            i = 0
            while True:
                try:
                    new_name = path + f" ({i})"
                    os.makedirs(new_name)
                    break
                except FileExistsError:
                    i += 1

    def remove(self):
        pass

    def archive_folder(self):
        pass

    def save_part(self):
        pass

    def save(self):
        pass

    def delete_parts(self):
        pass

    def move(self):
        pass

    def getExistingDirectory(self):
        pass

    def checkFolderUsable(self, path):
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")
        if not os.access(path, os.R_OK):
            raise ValueError(f"No read permission: {path}")
        if not os.access(path, os.W_OK):
            raise ValueError(f"No write permission: {path}")

        return {
            "path": path,
            "readable": True,
            "writable": True,
        }

    def getFolderContent(self, path):
        entries = []
        for entry in os.scandir(path):
            stat = entry.stat()
            item = {
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": self._dir_size(entry.path) if entry.is_dir() else stat.st_size,
                "modified_at": stat.st_mtime,
                "created_at": stat.st_ctime,
            }
            if entry.is_dir():
                item["children"] = self.getFolderContent(entry.path)
            entries.append(item)
        return entries

    def _dir_size(self, path):
        total = 0
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += self._dir_size(entry.path)
        return total

    def get_parts(self):
        pass
