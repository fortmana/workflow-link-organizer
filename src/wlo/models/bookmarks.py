from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, field_validator


class BrowserProfile(BaseModel):
    browser: Literal["chrome", "edge"]
    profile_dir: str
    display_name: str
    active: bool = True


class LinkBase(BaseModel):
    name: str
    path: str
    link_type: Literal["url", "folder"] | None = None
    browser: Literal["chrome", "edge"] | None = None
    profile_dir: str | None = None
    notes: str | None = None
    sort_order: int = 0


class LinkCreate(LinkBase):
    project_id: int


class LinkUpdate(BaseModel):
    name: str | None = None
    path: str | None = None
    link_type: Literal["url", "folder"] | None = None
    browser: Literal["chrome", "edge"] | None = None
    profile_dir: str | None = None
    notes: str | None = None
    sort_order: int | None = None
    project_id: int | None = None


class Link(BaseModel):
    id: int
    project_id: int
    name: str
    path: str
    link_type: Literal["url", "folder"]
    browser: str | None
    profile_dir: str | None
    notes: str | None
    sort_order: int
    created_at: str
    last_opened: str | None


class ProjectCreate(BaseModel):
    name: str
    color: str = "#4A90D9"
    default_browser: Literal["chrome", "edge"] | None = None
    default_profile_dir: str | None = None
    default_profile_name: str | None = None
    sort_order: int = 0
    column_index: int = 0

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not v.startswith("#") or len(v) not in (4, 7):
            raise ValueError("color must be a hex color")
        return v


class ProjectUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    default_browser: Literal["chrome", "edge"] | None = None
    default_profile_dir: str | None = None
    default_profile_name: str | None = None
    sort_order: int | None = None
    column_index: int | None = None


class Project(BaseModel):
    id: int
    name: str
    color: str
    default_browser: str | None
    default_profile_dir: str | None
    default_profile_name: str | None
    sort_order: int
    column_index: int = 0
    created_at: str
    links: list[Link] = []
