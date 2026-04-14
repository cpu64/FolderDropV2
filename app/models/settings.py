import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from platformdirs import user_config_dir

APP_NAME = "folderdrop"

CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = CONFIG_DIR / "app.db"

# ------------------------
# Data (Settings)
# ------------------------
@dataclass
class Settings:
    password: str
    port: int
    path: str
    allow_upload: bool
    allow_download: bool
    allow_rename: bool
    allow_delete: bool


# ------------------------
# DB Layer
# ------------------------
class SettingsDB:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._ensure_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    password TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    allow_upload INTEGER NOT NULL,
                    allow_download INTEGER NOT NULL,
                    allow_rename INTEGER NOT NULL,
                    allow_delete INTEGER NOT NULL
                )
                """
            )

            # Ensure single row exists
            cur = conn.execute("SELECT COUNT(*) FROM settings")
            count = cur.fetchone()[0]

            if count == 0:
                conn.execute(
                    """
                    INSERT INTO settings (
                        id, password, port, path,
                        allow_upload, allow_download,
                        allow_rename, allow_delete
                    )
                    VALUES (1, '', 5000, '.', 1, 1, 1, 0)
                    """
                )

    # ------------------------
    # CRUD
    # ------------------------
    def get(self) -> Settings:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM settings WHERE id = 1")
            row = cur.fetchone()

            if not row:
                raise RuntimeError("Settings row missing")

            return Settings(
                password=row[1],
                port=row[2],
                path=row[3],
                allow_upload=bool(row[4]),
                allow_download=bool(row[5]),
                allow_rename=bool(row[6]),
                allow_delete=bool(row[7]),
            )

    def update(self, settings: Settings):
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE settings SET
                    password = ?,
                    port = ?,
                    path = ?,
                    allow_upload = ?,
                    allow_download = ?,
                    allow_rename = ?,
                    allow_delete = ?
                WHERE id = 1
                """,
                (
                    settings.password,
                    settings.port,
                    settings.path,
                    int(settings.allow_upload),
                    int(settings.allow_download),
                    int(settings.allow_rename),
                    int(settings.allow_delete),
                ),
            )

    def patch(self, **kwargs):
        """
        Partial update (only provided fields)
        Example: db.patch(port=8000, allow_upload=False)
        """
        allowed = {
            "password",
            "port",
            "path",
            "allow_upload",
            "allow_download",
            "allow_rename",
            "allow_delete",
        }

        fields = []
        values = []

        for key, value in kwargs.items():
            if key not in allowed:
                continue

            fields.append(f"{key} = ?")

            if isinstance(value, bool):
                value = int(value)

            values.append(value)

        if not fields:
            return

        query = f"UPDATE settings SET {', '.join(fields)} WHERE id = 1"

        with self._connect() as conn:
            conn.execute(query, values)
