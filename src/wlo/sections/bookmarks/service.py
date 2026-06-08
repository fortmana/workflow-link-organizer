from __future__ import annotations
import json
import os
import re
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from wlo.config import BROWSER_EXES, BROWSER_USER_DATA
from wlo.db.connection import get_db
from wlo.models.bookmarks import (
    BrowserProfile, Link, LinkCreate, LinkUpdate,
    Project, ProjectCreate, ProjectUpdate,
)

_DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0)


# ── Browser profile enumeration ────────────────────────────────────────────

def list_profiles() -> list[BrowserProfile]:
    """Enumerate Chrome + Edge profiles, applying any saved custom labels and active state."""
    raw = _scan_profiles()
    try:
        with get_db() as db:
            overrides = {
                (r["browser"], r["profile_dir"]): {"label": r["label"], "active": bool(r["active"])}
                for r in db.execute("SELECT browser, profile_dir, label, active FROM profile_overrides")
            }
    except Exception:
        overrides = {}

    for p in raw:
        override = overrides.get((p.browser, p.profile_dir))
        if override:
            if override["label"]:
                p.display_name = override["label"]
            p.active = override["active"]
    return raw


def set_profile_label(browser: str, profile_dir: str, label: str) -> None:
    """Save a custom label for a profile. Empty label clears the label (keeps row if active=0)."""
    with get_db() as db:
        if label.strip():
            db.execute(
                """INSERT INTO profile_overrides (browser, profile_dir, label, active)
                   VALUES (?, ?, ?, 1)
                   ON CONFLICT(browser, profile_dir) DO UPDATE SET label = excluded.label""",
                (browser, profile_dir, label.strip()),
            )
        else:
            db.execute(
                "UPDATE profile_overrides SET label = '' WHERE browser = ? AND profile_dir = ?",
                (browser, profile_dir),
            )
            # Remove rows that have no meaningful data (no label, active=1 = default state)
            db.execute(
                "DELETE FROM profile_overrides WHERE browser = ? AND profile_dir = ? AND active = 1",
                (browser, profile_dir),
            )


def set_profile_active(browser: str, profile_dir: str, active: bool) -> None:
    """Mark a profile active or inactive. Inactive profiles are hidden from dropdowns."""
    with get_db() as db:
        if active:
            db.execute(
                "UPDATE profile_overrides SET active = 1 WHERE browser = ? AND profile_dir = ?",
                (browser, profile_dir),
            )
            # Clean up rows with no data (label='', active=1 means default — no row needed)
            db.execute(
                "DELETE FROM profile_overrides WHERE browser = ? AND profile_dir = ? AND label = '' AND active = 1",
                (browser, profile_dir),
            )
        else:
            db.execute(
                """INSERT INTO profile_overrides (browser, profile_dir, label, active)
                   VALUES (?, ?, '', 0)
                   ON CONFLICT(browser, profile_dir) DO UPDATE SET active = 0""",
                (browser, profile_dir),
            )


def _scan_profiles() -> list[BrowserProfile]:
    results: list[BrowserProfile] = []
    for browser, base in BROWSER_USER_DATA.items():
        if not base.exists():
            continue
        for entry in sorted(base.iterdir()):
            if not entry.is_dir():
                continue
            if not re.match(r"^(Default|Profile \d+)$", entry.name):
                continue
            prefs = entry / "Preferences"
            if not prefs.exists():
                continue
            try:
                data = json.loads(prefs.read_text(encoding="utf-8", errors="replace"))
                chrome_name = data.get("profile", {}).get("name", entry.name)
            except Exception:
                chrome_name = entry.name
            results.append(BrowserProfile(
                browser=browser,
                profile_dir=entry.name,
                display_name=chrome_name,
            ))
    return results


# ── Projects ───────────────────────────────────────────────────────────────

def list_projects() -> list[Project]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM projects ORDER BY sort_order, id"
        ).fetchall()
        projects = []
        for row in rows:
            link_rows = db.execute(
                "SELECT * FROM links WHERE project_id = ? ORDER BY sort_order, id",
                (row["id"],),
            ).fetchall()
            projects.append(_project_from_row(row, link_rows))
        return projects


def get_project(project_id: int) -> Project | None:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if not row:
            return None
        link_rows = db.execute(
            "SELECT * FROM links WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        ).fetchall()
        return _project_from_row(row, link_rows)


def create_project(data: ProjectCreate) -> Project:
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO projects
               (name, color, default_browser, default_profile_dir, default_profile_name, sort_order, column_index)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data.name, data.color, data.default_browser,
             data.default_profile_dir, data.default_profile_name, data.sort_order, data.column_index),
        )
        project_id = cur.lastrowid
    return get_project(project_id)


def update_project(project_id: int, data: ProjectUpdate) -> Project | None:
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return get_project(project_id)
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_db() as db:
        db.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            (*fields.values(), project_id),
        )
    return get_project(project_id)


def delete_project(project_id: int) -> bool:
    with get_db() as db:
        cur = db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cur.rowcount > 0


# ── Links ──────────────────────────────────────────────────────────────────

def create_link(data: LinkCreate) -> Link:
    path = _normalize_path(data.path)
    link_type = data.link_type or _detect_type(path)
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO links
               (project_id, name, path, link_type, browser, profile_dir, notes, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.project_id, data.name, path, link_type,
             data.browser, data.profile_dir, data.notes, data.sort_order),
        )
        link_id = cur.lastrowid
    return _get_link(link_id)


def update_link(link_id: int, data: LinkUpdate) -> Link | None:
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return _get_link(link_id)
    if "path" in fields and "link_type" not in fields:
        fields["path"] = _normalize_path(fields["path"])
        fields["link_type"] = _detect_type(fields["path"])
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_db() as db:
        db.execute(
            f"UPDATE links SET {set_clause} WHERE id = ?",
            (*fields.values(), link_id),
        )
    return _get_link(link_id)


def delete_link(link_id: int) -> bool:
    with get_db() as db:
        cur = db.execute("DELETE FROM links WHERE id = ?", (link_id,))
        return cur.rowcount > 0


def open_link(link_id: int) -> bool:
    with get_db() as db:
        link_row = db.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
        if not link_row:
            return False
        proj_row = db.execute(
            "SELECT * FROM projects WHERE id = ?", (link_row["project_id"],)
        ).fetchone()

        link_type = link_row["link_type"]
        path = link_row["path"]

        # Resolve browser + profile (link overrides project default)
        browser = link_row["browser"] or (proj_row["default_browser"] if proj_row else None)
        profile_dir = link_row["profile_dir"] or (proj_row["default_profile_dir"] if proj_row else None)

        if link_type == "folder":
            subprocess.Popen(["explorer.exe", path], creationflags=_DETACHED)
        elif browser and profile_dir and browser in BROWSER_EXES:
            exe = str(BROWSER_EXES[browser])
            subprocess.Popen(
                [exe, f"--profile-directory={profile_dir}", path],
                creationflags=_DETACHED,
            )
        else:
            webbrowser.open(path)

        db.execute(
            "UPDATE links SET last_opened = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
            (link_id,),
        )
    return True


# ── Quick-add ──────────────────────────────────────────────────────────────

def quick_add_link(url: str, name: str | None, project: str | int | None) -> Link:
    """Add a link by resolving project by name/ID or falling back to the default config."""
    path = _normalize_path(url)
    link_name = name or _infer_name(path)
    project_id = _resolve_project(project)
    if project_id is None:
        raise ValueError("No project specified and bookmarks.default_project_id is not configured.")
    return create_link(LinkCreate(project_id=project_id, name=link_name, path=path))


def _infer_name(path: str) -> str:
    try:
        host = urlparse(path).hostname or path
        return host.removeprefix("www.")
    except Exception:
        return path


def _resolve_project(project: str | int | None) -> int | None:
    from wlo.db.config_store import get_config
    if project is not None:
        if isinstance(project, int):
            return project
        try:
            return int(project)
        except (ValueError, TypeError):
            pass
        with get_db() as db:
            row = db.execute(
                "SELECT id FROM projects WHERE lower(name) = lower(?)", (project,)
            ).fetchone()
            return row["id"] if row else None
    default = get_config("bookmarks.default_project_id")
    if default is None:
        return None
    # Stored value may be a name (string) or an ID (int) — resolve either
    if isinstance(default, int):
        return default
    try:
        return int(default)
    except (ValueError, TypeError):
        pass
    with get_db() as db:
        row = db.execute(
            "SELECT id FROM projects WHERE lower(name) = lower(?)", (str(default),)
        ).fetchone()
        return row["id"] if row else None


# ── Helpers ────────────────────────────────────────────────────────────────

def _looks_like_url(path: str) -> bool:
    """True for bare hostnames/domains that have no scheme yet."""
    if re.match(r'^[A-Za-z]:[/\\]', path):   # C:\ or C:/
        return False
    if path.startswith(('\\\\', '//', '/')):   # UNC or Unix path
        return False
    return '.' in path                          # has a dot → likely a domain


def _normalize_path(path: str) -> str:
    """Prepend https:// to bare hostnames so they open as URLs."""
    if path.startswith(("http://", "https://", "ftp://")):
        return path
    if _looks_like_url(path):
        return "https://" + path
    return path


def _detect_type(path: str) -> str:
    if path.startswith(("http://", "https://", "ftp://")):
        return "url"
    if _looks_like_url(path):
        return "url"
    return "folder"


def _get_link(link_id: int) -> Link | None:
    with get_db() as db:
        row = db.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
        return _link_from_row(row) if row else None


def _link_from_row(row) -> Link:
    return Link(
        id=row["id"],
        project_id=row["project_id"],
        name=row["name"],
        path=row["path"],
        link_type=row["link_type"],
        browser=row["browser"],
        profile_dir=row["profile_dir"],
        notes=row["notes"],
        sort_order=row["sort_order"],
        created_at=row["created_at"],
        last_opened=row["last_opened"],
    )


def _project_from_row(row, link_rows) -> Project:
    return Project(
        id=row["id"],
        name=row["name"],
        color=row["color"],
        default_browser=row["default_browser"],
        default_profile_dir=row["default_profile_dir"],
        default_profile_name=row["default_profile_name"],
        sort_order=row["sort_order"],
        column_index=dict(row).get("column_index", 0),
        created_at=row["created_at"],
        links=[_link_from_row(lr) for lr in link_rows],
    )
