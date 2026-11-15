from flask import Blueprint, render_template, redirect, url_for, flash, abort
from .extensions import db
from .models import User
from .utils import login_required, admin_required, current_user

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=all_users)


@bp.get("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    u = User.query.get_or_404(user_id)
    return render_template("admin_user_detail.html", user=u)


def _guard_self(user_id):
    if user_id == current_user().id:
        flash("Tidak bisa mengelola akun sendiri.", "warning")
        return False
    return True


@bp.post("/users/<int:user_id>/toggle")
@login_required
@admin_required
def toggle_active(user_id):
    if not _guard_self(user_id):
        return redirect(url_for("admin.users"))
    u = User.query.get_or_404(user_id)
    u.is_active = not u.is_active
    db.session.commit()
    flash("Status akun diperbarui.", "success")
    return redirect(url_for("admin.users"))


@bp.post("/users/<int:user_id>/delete")
@login_required
@admin_required
def delete_user(user_id):
    if not _guard_self(user_id):
        return redirect(url_for("admin.users"))
    u = User.query.get_or_404(user_id)
    db.session.delete(u)  # cascade notes
    db.session.commit()
    flash("Akun dan catatannya dihapus.", "info")
    return redirect(url_for("admin.users"))
