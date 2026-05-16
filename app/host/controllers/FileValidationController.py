import ctypes
import os
import platform
import re
import psutil


class FileValidationController:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors = []

    def validate_path(self) -> bool:
        if self.is_absolute_path(self.filepath):
            return False
        parts = self.split_path_into_parts()
        for part in parts:
            if part == "..":
                self.register_error("Path must not contain '..'")
            else:
                if self.verify_path_against_os(part):
                    if not self.verify_path_against_file_system(part):
                        self.register_error(f"Path part '{part}' isn't valid in this file system.")
                else:
                    self.register_error(f"Path part '{part}' is not valid on this OS.")

        return len(self.errors) == 0

    def is_absolute_path(self, filepath) -> bool:
        if not os.path.isabs(filepath):
            return False
        self.register_error("Path must not be absolute.")
        return True

    def split_path_into_parts(self) -> list:
        return self.filepath.strip("/").split("/")

    def register_error(self, message: str):
        self.errors.append(message)

    def verify_path_against_os(self, part) -> bool:
        if not part:
            return False

        if "\x00" in part:
            return False

        if platform.system() == "Windows":
            forbidden = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
            if forbidden.search(part):
                return False

            reserved = re.compile(
                r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..+)?$',
                re.IGNORECASE,
            )
            if reserved.match(part):
                return False

        return True

    def verify_path_against_file_system(self, part, directory=".") -> bool:
        if not part:
            return False

        path = os.path.abspath(directory)
        best_match = ""
        fs_type = "unknown"

        for partition in psutil.disk_partitions(all=True):
            if path.startswith(partition.mountpoint):
                if len(partition.mountpoint) > len(best_match):
                    best_match = partition.mountpoint
                    fs_type = partition.fstype

        fs_type = fs_type.upper()

        try:
            if platform.system() == "Windows":
                max_len = ctypes.c_ulong()
                root = os.path.splitdrive(os.path.abspath(directory))[0] + "\\"
                ctypes.windll.kernel32.GetVolumeInformationW(
                    root, None, 0, None, ctypes.byref(max_len), None, None, 0
                )
                max_len = max_len.value
            else:
                max_len = os.statvfs(directory).f_namemax
        except Exception:
            max_len = 255

        if len(part.encode("utf-8")) > max_len:
            return False

        if "FAT" in fs_type or "NTFS" in fs_type:
            if part.endswith(".") or part.endswith(" "):
                return False
            if re.compile(r'[<>:"/\\|?*\x00-\x1f]').search(part):
                return False

        return True
