from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from .models import User


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        u = current_user()
        if not u or not u.is_active:
            session.clear()
            return redirect(url_for("auth.login", next=request.path))
        return view(*a, **kw)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        u = current_user()
        if not u or u.role != "admin":
            abort(403)
        return view(*a, **kw)
    return wrapped
