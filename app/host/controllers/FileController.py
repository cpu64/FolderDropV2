from app.host.interfaces.OwnerFileSystemInterface import OwnerFileSystemInterface


class FileController:
    def __init__(self):
        self.owner_fs = OwnerFileSystemInterface()

    def on_deleted(self):
        pass

    def on_created(self):
        pass

    def on_modified(self):
        pass

    def on_moved(self):
        pass

    def checkFolderUsable(self, path):
        return self.owner_fs.checkFolderUsable(path)

    def getFolderContent(self, path):
        return self.owner_fs.getFolderContent(path)
