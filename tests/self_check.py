"""Minimal runnable checks for core security logic (no frameworks). Run: python tests/self_check.py"""
import base64, os, sys, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# SEC-03: AES-256-GCM encrypt/decrypt + fresh nonce
os.environ["NOTES_ENCRYPTION_KEY_B64"] = base64.b64encode(os.urandom(32)).decode()
from app.crypto import encrypt, decrypt
msg = "rahasia 🔒"
b1, b2 = encrypt(msg), encrypt(msg)
assert decrypt(b1) == msg and decrypt(b2) == msg
assert b1[:12] != b2[:12], "nonce must be random per encryption"
assert b1 != b2

# SEC-02: bcrypt hash & verify, no plaintext
from app.models import User
u = User(username="u", email="u@e.test", role="user")
u.set_password("s3cret-pass")
assert u.password_hash != b"s3cret-pass"
assert u.check_password("s3cret-pass") and not u.check_password("wrong")

# DB + ownership logic smoke (Flask-SQLAlchemy)
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")
os.environ["SECRET_KEY"] = "test"
from app import create_app
from app.extensions import db
from app.models import Note
app = create_app()
with app.app_context():
    u2 = User(username="u2", email="u2@e.test", role="user"); u2.set_password("pw12345678")
    db.session.add(u2); db.session.commit()
    n = Note(user_id=u2.id, title="t", encrypted_content=encrypt("isi"))
    db.session.add(n); db.session.commit()
    assert Note.query.filter_by(user_id=u2.id, id=n.id).one().title == "t"
    assert decrypt(Note.query.get(n.id).encrypted_content) == "isi"

print("self_check: OK")
