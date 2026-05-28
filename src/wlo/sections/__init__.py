from flask import Flask


def register_all(app: Flask) -> None:
    from wlo.sections.bookmarks.routes import bp as bookmarks_bp
    from wlo.sections.config.routes import bp as config_bp
    app.register_blueprint(bookmarks_bp)
    app.register_blueprint(config_bp)

