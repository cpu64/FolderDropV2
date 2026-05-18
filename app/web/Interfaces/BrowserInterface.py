import os

from quart import send_file

# 60.1 šitos klasės net nėra diagramoje
class BrowserInterface:
    async def download(self, full_path: str, filename: str):
        return await send_file(
            full_path,
            as_attachment=True,
            attachment_filename=filename,
            mimetype="application/octet-stream",
        )
