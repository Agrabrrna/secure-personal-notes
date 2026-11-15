from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .extensions import db
from .models import User
from .utils import login_required, current_user

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not (3 <= len(username) <= 80 and "@" in email and len(password) >= 8):
            flash("Input tidak valid (username>=3, email valid, password>=8).", "danger")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username/email sudah digunakan.", "danger")
        else:
            u = User(username=username, email=email, role="user", is_active=True)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash("Registrasi berhasil, silakan login.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        u = User.query.filter_by(username=username).first()
        if not u or not u.check_password(password):
            flash("Kredensial salah.", "danger")
        elif not u.is_active:
            flash("Akun nonaktif.", "danger")
        else:
            session.clear()
            session["user_id"] = u.id
            session.permanent = True
            return redirect(request.args.get("next") or url_for("notes.dashboard"))
    return render_template("login.html")


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Logout berhasil.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile/password", methods=["GET", "POST"])
@login_required
def change_password():
    u = current_user()
    if request.method == "POST":
        old = request.form.get("old_password") or ""
        new = request.form.get("new_password") or ""
        if not u.check_password(old):
            flash("Password lama salah.", "danger")
        elif len(new) < 8:
            flash("Password baru minimal 8 karakter.", "danger")
        else:
            u.set_password(new)
            db.session.commit()
            flash("Password diperbarui.", "success")
            return redirect(url_for("notes.dashboard"))
    return render_template("change_password.html")
