from __future__ import annotations

from flask import Flask, redirect, render_template, url_for
from flask_login import current_user

from .config import Config
from .extensions import csrf, db, login_manager, migrate
from version import VERSION


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melden Sie sich an."

    register_blueprints(app)
    register_error_handlers(app)
    register_shell_context(app)
    app.jinja_env.globals["app_version"] = VERSION

    @app.get("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("index.html")

    @app.get("/impressum")
    def impressum():
        return render_template("legal/impressum.html")

    @app.get("/datenschutz")
    def datenschutz():
        return render_template("legal/datenschutz.html")

    return app


def register_blueprints(app: Flask) -> None:
    from .admin.routes import bp as admin_bp
    from .auth.routes import bp as auth_bp
    from .dashboard.routes import bp as dashboard_bp
    from .exports.routes import bp as exports_bp
    from .layouts.routes import bp as layouts_bp
    from .tools.api import bp as tools_api_bp
    from .tools.routes import bp as tools_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(tools_api_bp)
    app.register_blueprint(layouts_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(admin_bp)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def too_large(error):
        return render_template("errors/413.html"), 413


def register_shell_context(app: Flask) -> None:
    @app.shell_context_processor
    def make_shell_context():
        return {"db": db}
