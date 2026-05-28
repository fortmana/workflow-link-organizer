import json
from typing import Any
from wlo.db.connection import get_db

_DEFAULTS: dict[str, tuple[Any, str]] = {
    "bookmarks.default_browser": (
        "chrome",
        "Default browser when creating a new project.",
    ),
    "bookmarks.default_project_id": (
        None,
        "Default project for quick-add links. Set to a project name (e.g. 'Inbox') or its numeric ID.",
    ),
    "bookmarks.column_width": (
        320,
        "Width in pixels for each project column. Increase for wider cards, decrease to fit more columns.",
    ),
}


def seed_config_defaults() -> None:
    with get_db() as db:
        for key, (value, description) in _DEFAULTS.items():
            db.execute(
                "INSERT OR IGNORE INTO config (key, value, description) VALUES (?, ?, ?)",
                (key, json.dumps(value), description),
            )


def get_config(key: str, default: Any = None) -> Any:
    with get_db() as db:
        row = db.execute(
            "SELECT value FROM config WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return default


def set_config(key: str, value: Any) -> None:
    with get_db() as db:
        db.execute(
            """INSERT INTO config (key, value)
               VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE
               SET value = excluded.value,
                   updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')""",
            (key, json.dumps(value)),
        )


def get_all_config() -> dict[str, dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT key, value, description, updated_at FROM config ORDER BY key"
        ).fetchall()
        result = {}
        for row in rows:
            try:
                val = json.loads(row["value"])
            except (ValueError, TypeError):
                val = None
            result[row["key"]] = {
                "value": val,
                "description": row["description"],
                "updated_at": row["updated_at"],
            }
        return result

