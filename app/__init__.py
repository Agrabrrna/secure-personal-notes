import os
from datetime import timedelta
from flask import Flask
from .extensions import db
from .models import User


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-insecure-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=int(os.environ.get("SESSION_IDLE_MINUTES", "30"))),
    )
    db.init_app(app)

    from .auth import bp as auth_bp
    from .notes import bp as notes_bp
    from .admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_user():
        from .utils import current_user
        return {"current_user": current_user}

    with app.app_context():
        db.create_all()
        _ensure_admin(app)

    @app.get("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("notes.dashboard"))

    return app


def _ensure_admin(app):
    # ponytail: bootstrap admin via env for first run; upgrade to CLI/installer when needed.
    username = os.environ.get("BOOTSTRAP_ADMIN_USER")
    password = os.environ.get("BOOTSTRAP_ADMIN_PASS")
    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "admin@example.local")
    if not (username and password):
        return
    if User.query.filter_by(username=username).first():
        return
    u = User(username=username, email=email, role="admin", is_active=True)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
