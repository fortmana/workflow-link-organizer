from pathlib import Path
from flask import Flask, send_from_directory, jsonify

from wlo.logging_setup import configure_logging
from wlo.db.connection import init_db
from wlo.db.migrations import apply_migrations
from wlo.db.config_store import seed_config_defaults

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> Flask:
    configure_logging()

    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

    init_db()
    apply_migrations()
    seed_config_defaults()

    from wlo.sections import register_all
    register_all(app)

    @app.get("/")
    def index():
        return send_from_directory(str(STATIC_DIR), "index.html")

    @app.get("/health")
    def health():
        from wlo.config import PORT
        return jsonify({"status": "ok", "port": PORT})

    return app


def _run_dev() -> None:
    """Entry point for `wlo-dev` - Flask dev server with auto-reloader."""
    import os
    os.environ.setdefault("WLO_DEV", "1")
    from wlo.config import PORT, HOST
    app = create_app()
    app.run(host=HOST, port=PORT, debug=True, use_reloader=True)


def _run_prod() -> None:
    """Production entry point - uses Waitress (multi-threaded WSGI server)."""
    import os
    os.environ["WLO_DEV"] = "0"
    from wlo.config import PORT, HOST
    from waitress import serve
    app = create_app()
    serve(app, host=HOST, port=PORT, threads=8, channel_timeout=600)


if __name__ == "__main__":
    import os
    if os.environ.get("WLO_DEV", "1") == "0":
        _run_prod()
    else:
        _run_dev()

