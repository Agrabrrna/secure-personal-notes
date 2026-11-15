# SEC-01 Risk Assessment

| Aset | Ancaman | Kelemahan | Dampak | CIA | Kontrol (terkait) |
|---|---|---|---|---|---|
| Akun pengguna (username/email/role) | Credential stuffing, brute force | Password lemah/tanpa hash kuat | Akses tidak sah | C,I | SEC-02 bcrypt, SEC-10 sesi/logout, SEC-05 pembatasan login gagal |
| Password (kredensial) | Pencurian DB | Penyimpanan plaintext/hash lemah | Kompromi akun massal | C,I | SEC-02 bcrypt+salt unik, tidak ada plaintext di DB/log |
| Isi catatan pribadi | Kebocoran DB/backup | Data at-rest plaintext | Pelanggaran privasi | C | SEC-03 AES-256-GCM (nonce unik), kunci di luar source/DB, SEC-07 backup terenkripsi |
| Kunci enkripsi & SECRET_KEY | Pencurian file config | Permission longgar, commit ke repo | Dekripsi massal/hijack sesi | C,I | `.env`/`config/` di luar repo, permission ketat (SEC-05), rotasi terencana |
| Sesi login (cookie) | Session hijacking/fixation | Cookie tanpa flag aman, sesi tak invalid | Akses akun korban | C,I | SEC-04 HTTPS, cookie HttpOnly/Secure/SameSite=Lax, timeout idle 30m, logout hapus sesi (SEC-10) |
| Database SQLite | SQL Injection, akses file | Query string concat, permission file | Bocor/ubah/hapus data | C,I,A | SEC-08 prepared statement/ORM, permission ketat, backup (SEC-07) |
| Data input user (judul/isi) | Stored/Reflected XSS | Output tanpa escaping | Pencurian sesi, deface | C,I | SEC-09 auto-escaping Jinja di semua tampilan, validasi server-side |
| Kepemilikan catatan & role admin | IDOR, privilege escalation | Cek otorisasi di client saja | Akses/ubah data orang lain | C,I | SEC-10 cek kepemilikan & role server-side tiap aksi, tidak bisa kelola diri sendiri |
| Server/VM & layanan | Intrusi jaringan, service abuse | Port terbuka, SSH lemah, service root | Kompromi sistem | C,I,A | SEC-05 hardening+fail2ban, SEC-06 UFW default deny, SEC-04 HTTPS via Nginx |
| Backup data | Kehilangan/ransomware/corrupt | Tanpa backup/restore uji, backup plaintext | Kehilangan data permanen | A,(C) | SEC-07 backup otomatis terenkripsi, permission ketat, prosedur restore teruji |

Terkait implementasi app: SEC-02 (`app/models.py`), SEC-03 (`app/crypto.py`), SEC-08 (SQLAlchemy ORM/parameterized), SEC-09 (Jinja autoescape), SEC-10 (`app/utils.py`, cek owner di `app/notes.py`, role di `app/admin.py`).
