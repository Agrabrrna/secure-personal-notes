from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import or_
from .extensions import db
from .models import Note
from .utils import login_required, current_user
from .crypto import encrypt, decrypt

bp = Blueprint("notes", __name__)


@bp.get("/dashboard")
@login_required
def dashboard():
    u = current_user()
    total = Note.query.filter_by(user_id=u.id).count()
    recent = Note.query.filter_by(user_id=u.id).order_by(Note.updated_at.desc()).limit(5).all()
    return render_template("dashboard.html", total=total, recent=recent)


@bp.route("/notes")
@login_required
def list_notes():
    u = current_user()
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1) or 1), 1)
    query = Note.query.filter_by(user_id=u.id)
    if q:
        query = query.filter(Note.title.ilike(f"%{q}%"))  # search title only (content encrypted)
    pagination = query.order_by(Note.updated_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("notes_list.html", pagination=pagination, q=q)


def _get_owned(note_id: int) -> Note:
    n = Note.query.get_or_404(note_id)
    if n.user_id != current_user().id:
        abort(403)
    return n


@bp.route("/notes/new", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = request.form.get("content") or ""
        if not title:
            flash("Judul wajib diisi.", "danger")
        else:
            n = Note(user_id=current_user().id, title=title, encrypted_content=encrypt(content))
            db.session.add(n)
            db.session.commit()
            flash("Catatan dibuat.", "success")
            return redirect(url_for("notes.detail", note_id=n.id))
    return render_template("note_form.html", note=None)


@bp.get("/notes/<int:note_id>")
@login_required
def detail(note_id):
    n = _get_owned(note_id)
    try:
        content = decrypt(n.encrypted_content)
    except Exception:
        content = "[gagal dekripsi: cek NOTES_ENCRYPTION_KEY_B64]"
    return render_template("note_detail.html", note=n, content=content)


@bp.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    n = _get_owned(note_id)
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = request.form.get("content") or ""
        if not title:
            flash("Judul wajib diisi.", "danger")
        else:
            n.title = title
            n.encrypted_content = encrypt(content)  # new nonce each save
            db.session.commit()
            flash("Catatan diperbarui.", "success")
            return redirect(url_for("notes.detail", note_id=n.id))
    try:
        content = decrypt(n.encrypted_content)
    except Exception:
        content = ""
    return render_template("note_form.html", note=n, content=content)


@bp.post("/notes/<int:note_id>/delete")
@login_required
def delete(note_id):
    n = _get_owned(note_id)
    db.session.delete(n)
    db.session.commit()
    flash("Catatan dihapus.", "info")
    return redirect(url_for("notes.list_notes"))
