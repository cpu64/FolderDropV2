from __future__ import annotations

from pathlib import Path
import secrets
import shutil

class FilePart:
    def __init__( self, temp_folder: str | Path, filepath: str, part_count: int, ):
        self.temp_folder = Path(temp_folder)
        self.filepath = filepath
        self.part_count = part_count

        self.temp_folder.mkdir(parents=True, exist_ok=True)

        # {part_number: Path}
        self.parts: dict[int, Path] = {}

    def save_part(self, part_number: int, data: bytes) -> str:
        random_name = secrets.token_hex(16) + ".part"

        part_path = self.temp_folder / random_name

        with open(part_path, "wb") as f:
            f.write(data)

        self.parts[part_number] = part_path

        return random_name

    def save_file(self, output_folder: str | Path) -> Path:
        if len(self.parts) != self.part_count:
            raise ValueError(
                f"Expected {self.part_count} parts, "
                f"got {len(self.parts)}"
            )

        output_folder = Path(output_folder)

        final_path = output_folder / self.filepath

        with open(final_path, "wb") as outfile:
            for part_number in range(self.part_count):

                if part_number not in self.parts:
                    raise ValueError(
                        f"Missing part {part_number}"
                    )

                part_path = self.parts[part_number]

                with open(part_path, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)

        return final_path

    def delete_parts(self) -> None:
        for part_path in self.parts.values():
            try:
                part_path.unlink(missing_ok=True)
            except Exception:
                pass

        self.parts.clear()
