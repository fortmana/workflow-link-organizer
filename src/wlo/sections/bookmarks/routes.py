from flask import Blueprint, jsonify, request
from wlo.sections.bookmarks.service import (
    list_profiles, list_projects, get_project,
    create_project, update_project, delete_project,
    create_link, update_link, delete_link, open_link,
    set_profile_label, set_profile_active, quick_add_link,
)
from wlo.models.bookmarks import (
    ProjectCreate, ProjectUpdate, LinkCreate, LinkUpdate,
)

bp = Blueprint("bookmarks", __name__)


@bp.get("/api/bookmarks/profiles")
def profiles():
    return jsonify([p.model_dump() for p in list_profiles()])


@bp.put("/api/bookmarks/profiles/<browser>/<path:profile_dir>")
def put_profile(browser: str, profile_dir: str):
    body = request.get_json() or {}
    if "label" in body:
        set_profile_label(browser, profile_dir, body.get("label", ""))
    if "active" in body:
        set_profile_active(browser, profile_dir, bool(body.get("active", True)))
    return jsonify({"ok": True})


@bp.get("/api/bookmarks/projects")
def get_projects():
    return jsonify([p.model_dump() for p in list_projects()])


@bp.post("/api/bookmarks/projects")
def post_project():
    data = ProjectCreate.model_validate(request.get_json())
    project = create_project(data)
    return jsonify(project.model_dump()), 201


@bp.get("/api/bookmarks/projects/<int:project_id>")
def get_project_route(project_id: int):
    project = get_project(project_id)
    if not project:
        return jsonify({"error": "not found"}), 404
    return jsonify(project.model_dump())


@bp.put("/api/bookmarks/projects/<int:project_id>")
def put_project(project_id: int):
    data = ProjectUpdate.model_validate(request.get_json())
    project = update_project(project_id, data)
    if not project:
        return jsonify({"error": "not found"}), 404
    return jsonify(project.model_dump())


@bp.delete("/api/bookmarks/projects/<int:project_id>")
def del_project(project_id: int):
    if not delete_project(project_id):
        return jsonify({"error": "not found"}), 404
    return "", 204


@bp.post("/api/bookmarks/links/quick")
def quick_add():
    body = request.get_json() or {}
    url = body.get("url")
    if not url:
        return jsonify({"error": "url is required"}), 400
    try:
        link = quick_add_link(url, body.get("name"), body.get("project"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(link.model_dump()), 201


@bp.post("/api/bookmarks/projects/<int:project_id>/links")
def post_link(project_id: int):
    body = request.get_json()
    body["project_id"] = project_id
    data = LinkCreate.model_validate(body)
    link = create_link(data)
    return jsonify(link.model_dump()), 201


@bp.put("/api/bookmarks/links/<int:link_id>")
def put_link(link_id: int):
    data = LinkUpdate.model_validate(request.get_json())
    link = update_link(link_id, data)
    if not link:
        return jsonify({"error": "not found"}), 404
    return jsonify(link.model_dump())


@bp.delete("/api/bookmarks/links/<int:link_id>")
def del_link(link_id: int):
    if not delete_link(link_id):
        return jsonify({"error": "not found"}), 404
    return "", 204


@bp.post("/api/bookmarks/links/<int:link_id>/open")
def open_link_route(link_id: int):
    if not open_link(link_id):
        return jsonify({"error": "not found"}), 404
    return jsonify({"opened": True})

