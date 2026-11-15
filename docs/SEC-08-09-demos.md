# SEC-08 SQL Injection & SEC-09 XSS — Demo rentan vs aman

> Cuplikan **rentan** hanya untuk bukti uji di lingkungan lab/VM terisolasi. **Jangan** dipakai di `app/`.

## SEC-08 SQL Injection

**Rentan (JANGAN dipakai):**
```python
# login vulnerable
cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password_hash='{pw}'")
# search vulnerable
cur.execute("SELECT * FROM notes WHERE title LIKE '%" + q + "%'")
```
Payload uji: `' OR '1'='1` pada login/pencarian → bypass/ekstraksi.

**Aman (dipakai di app):** ORM/parameterized, tanpa string concat input user.
```python
User.query.filter_by(username=username).first()
Note.query.filter(Note.title.ilike(f"%{q}%"))  # SQLAlchemy bind parameter
# raw: cur.execute("SELECT * FROM notes WHERE title LIKE ?", (f"%{q}%",))
```
Bukti: payload sama tidak mengubah logika query; bandingkan log/query plan.

## SEC-09 XSS

**Rentan (JANGAN dipakai):**
```html
<!-- menampilkan input mentah -->
<h3>{{ note.title|safe }}</h3>
<div>{{ content|safe }}</div>
```
Payload uji judul/isi: `<script>alert(1)</script>` atau `<img src=x onerror=alert(1)>` → eksekusi.

**Aman (dipakai di app):** Jinja autoescape default; variabel dirender sebagai teks (`{{ note.title }}`, `{{ content }}`), tanpa `|safe` pada data user. Header CSP dapat ditambah di Nginx/app sebagai lapisan tambahan.

Bukti: simpan payload sebagai judul/isi, tampilkan detail/list — muncul sebagai teks, tidak dieksekusi (cek DOM/network).
