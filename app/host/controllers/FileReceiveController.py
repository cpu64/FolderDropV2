from pathlib import Path
from tempfile import gettempdir
from quart import jsonify
from app.host.controllers.FileValidationController import FileValidationController
from app.models.FilePart import FilePart
from app.models.settings import settings_store

class FileReceiveController:
    def __init__(self):
        self.temp_folder = Path(gettempdir()) / "FolderDropV2"
        self.TemporaryFiles: dict[str, FilePart] = {}
        self.settings = settings_store.get_settings()

    def recieve_metadata(self, data):
        filepath = data.get("filepath")
        part_count = data.get("part_count")

        validator = FileValidationController(filepath)
        if not validator.validate_path():
            return jsonify({
                "ok": False,
                "error": validator.errors,
            }), 400

        upload = FilePart(
            temp_folder=self.temp_folder,
            filepath=filepath,
            part_count=part_count,
        )

        self.TemporaryFiles[filepath] = upload

        return jsonify({
            "ok": True,
            "filepath": filepath,
            "part_count": part_count,
        })


    def recieve_part(self, form, files):
        filepath = form.get("filepath")
        part_number = form.get("part_number")

        validator = FileValidationController(filepath)
        if not validator.validate_path():
            return jsonify({
                "ok": False,
                "error": validator.errors,
            }), 400

        part_number = int(part_number)
        upload = self.TemporaryFiles.get(filepath)

        upload.save_part(
            part_number=part_number,
            data=files["data"].read(),
        )

        received_count = len(upload.parts)

        is_complete = received_count == upload.part_count

        if is_complete:
            upload.save_file(self.settings.path)
            upload.delete_parts()
            del self.TemporaryFiles[filepath]

        return jsonify({
            "ok": True,
            "part_number": part_number,
            "received_parts": received_count,
            "completed": is_complete,
        })
