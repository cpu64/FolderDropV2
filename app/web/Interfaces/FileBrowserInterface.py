import os
import aiofiles

from quart import Response


class FileBrowserInterface:
    async def download(self, full_path: str, filename: str, on_complete=None):
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")

        async def generate():
            async with aiofiles.open(full_path, "rb") as f:
                while chunk := await f.read(65536):
                    yield chunk
            if on_complete:
                await on_complete()

        return Response(
            generate(),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/octet-stream",
            },
        )
