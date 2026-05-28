from flask import Blueprint, jsonify, request
from wlo.db.config_store import get_all_config, set_config

bp = Blueprint("config_api", __name__)


@bp.get("/api/config")
def get_config_route():
    return jsonify(get_all_config())


@bp.put("/api/config/<key>")
def put_config_route(key: str):
    body = request.get_json() or {}
    set_config(key, body.get("value"))
    return jsonify({"ok": True})

