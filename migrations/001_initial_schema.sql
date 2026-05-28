-- Workflow Link Organizer — initial schema.
-- Consolidated final state: projects, links, config, and profile_overrides.

CREATE TABLE IF NOT EXISTS projects (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT    NOT NULL,
    color                TEXT    NOT NULL DEFAULT '#4A90D9',
    default_browser      TEXT    CHECK(default_browser IN ('chrome', 'edge')),
    default_profile_dir  TEXT,
    default_profile_name TEXT,
    sort_order           INTEGER NOT NULL DEFAULT 0,
    column_index         INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    path        TEXT    NOT NULL,
    link_type   TEXT    NOT NULL DEFAULT 'url'
                        CHECK(link_type IN ('url', 'folder')),
    browser     TEXT    CHECK(browser IN ('chrome', 'edge')),
    profile_dir TEXT,
    notes       TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_opened TEXT
);

CREATE INDEX IF NOT EXISTS idx_links_project_id ON links(project_id);

CREATE TABLE IF NOT EXISTS config (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    description TEXT,
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS profile_overrides (
    browser     TEXT    NOT NULL CHECK(browser IN ('chrome', 'edge')),
    profile_dir TEXT    NOT NULL,
    label       TEXT    NOT NULL,
    active      INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (browser, profile_dir)
);
