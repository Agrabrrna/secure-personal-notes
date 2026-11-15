# Plan — Secure Personal Notes (sesuai PRD v1.0)

## Ringkasan
- **Produk:** Web app catatan pribadi aman (tugas Keamanan Sistem Komputer).
- **Stack (constraint PRD):** Python Flask, SQLite, HTML/CSS/JS/Bootstrap, Nginx, Ubuntu Linux (VirtualBox). Crypto/hash: bcrypt, AES-256-GCM, OpenSSL (self-signed). Firewall: UFW.
- **Role:** `User` (CRUD catatan milik sendiri), `Admin` (kelola akun; tidak boleh baca isi catatan).

## Fungsional (MVP / Must Have)
- [x] **Auth:** registrasi, login, logout, validasi input server-side, sesi (HttpOnly/Secure/SameSite=Lax, timeout idle 30m). (`app/auth.py`, `app/__init__.py`)
- [x] **User Dashboard:** total catatan, 5 terbaru, info user, navigasi; empty state. (`app/notes.py`, `templates/dashboard.html`)
- [x] **Notes:** create/read list/detail/update/delete + konfirmasi hapus (POST), pagination (10), pencarian **judul saja** (isi terenkripsi). Cek kepemilikan di server pada read/update/delete. (`app/notes.py`)
- [x] **User Management (Admin):** daftar & detail info pengguna (tanpa password_hash/isi catatan), nonaktifkan/aktifkan/hapus akun (dengan konfirmasi; tidak bisa kelola diri sendiri; hapus akun cascade catatan). (`app/admin.py`)
- [x] **Profil:** ganti password (verifikasi lama, hash baru). (`app/auth.py`)

## Keamanan — 10 persyaratan (Must Have, dengan bukti uji)
- [x] **SEC-01 Risk Assessment:** dokumen ≥5 aset (ancaman, kelemahan, dampak, CIA, kontrol) terhubung ke SEC-02..10. (`docs/SEC-01-risk-assessment.md`)
- [x] **SEC-02 Password Hashing:** bcrypt + salt unik; tidak ada plaintext di DB/log. (`app/models.py`)
- [x] **SEC-03 Data Encryption:** isi catatan AES-256-GCM, nonce acak 12 byte baru tiap simpan/edit, tag auth; kunci di luar source code & DB (`NOTES_ENCRYPTION_KEY_B64`). (`app/crypto.py`)
- [~] **SEC-04 HTTPS:** sertifikat self-signed OpenSSL via Nginx, HTTP→HTTPS redirect. (contoh config + langkah: `docs/SEC-04-05-06-07-infra.md`, `scripts/nginx-secure-personal-notes.conf.example` — eksekusi/bukti di Ubuntu/VM)
- [~] **SEC-05 Linux Hardening:** admin non-root, service account, permission ketat, SSH diperketat, pembatasan login gagal (fail2ban/setara), update sistem. (checklist: `docs/SEC-04-05-06-07-infra.md` — eksekusi/bukti di VM)
- [~] **SEC-06 Firewall:** UFW default deny, hanya port perlu (SSH/HTTPS[/HTTP redirect]); bukti Nmap sebelum & sesudah. (checklist: `docs/SEC-04-05-06-07-infra.md`)
- [~] **SEC-07 Backup & Restore:** backup otomatis terenkripsi (cron), permission ketat, prosedur restore terdokumentasi & diuji. (skrip + langkah: `scripts/backup.sh`, `docs/SEC-04-05-06-07-infra.md` — cron/restore uji di VM)
- [x] **SEC-08 SQL Injection:** prepared statement/ORM di semua query; demo **versi rentan vs aman** (login & pencarian). (`docs/SEC-08-09-demos.md`)
- [x] **SEC-09 XSS:** output escaping di semua titik tampil data user (Jinja autoescape); demo **versi rentan vs aman** (judul/isi). (`docs/SEC-08-09-demos.md`)
- [x] **SEC-10 IDOR & Session:** cek kepemilikan server-side (baca/ubah/hapus), cek role admin, logout hapus sesi, cookie HttpOnly/Secure(prod)/SameSite=Lax, timeout idle. (`app/utils.py`, `app/notes.py`, `app/admin.py`, `app/__init__.py`)

## Data (sesuai PRD)
- **users:** `id, username, email, password_hash, role(admin|user), is_active, created_at`
- **notes:** `id, user_id(FK), title, encrypted_content, created_at, updated_at` (1:N, cascade delete)

## Milestones
1. **Setup & desain** — struktur Flask, config/secret terpisah, skema SQLite, risk assessment (SEC-01).
2. **Auth & sesi** — register/login/logout/profile, bcrypt (SEC-02), validasi, manajemen sesi & role (SEC-10 dasar).
3. **Notes + crypto** — CRUD, pencarian judul, kepemilikan (IDOR), AES-256-GCM untuk isi (SEC-03).
4. **Admin & UI** — dashboard user/admin, user management, Bootstrap responsif, empty/error states, escaping (SEC-09).
5. **Infra & hardening** — Nginx+HTTPS (SEC-04), hardening (SEC-05), UFW+Nmap (SEC-06), backup/restore cron terenkripsi (SEC-07).
6. **Pengujian & bukti** — demo SQLi/XSS rentan vs aman (SEC-08/09), uji IDOR/sesi, bukti screenshot/tabel untuk semua SEC.

## Out of Scope (PRD)
- Sinkronisasi cloud, sharing/kolaborasi, mobile native, integrasi pihak ketiga/MFA/email, lampiran file, AI, pencarian isi catatan, CA publik/internet publik.

## Open Questions (perlu keputusan, PRD 18.4)
- Q1 pembuatan Admin awal; Q2 admin buat akun?; Q3 timeout sesi (asumsi 30m); Q4 limit login gagal/blokir; Q5 jadwal & retensi backup; Q6 enkripsi backup; Q7 trash vs hapus permanen (asumsi permanen); Q8 bentuk demo rentan/aman; Q9 format laporan/bukti.

<!-- ponytail: scaffold MVP app-level + docs/skrip infra selesai. [~]=butuh eksekusi & bukti screenshot/log di Ubuntu/VM (Nginx/UFW/hardening/cron/Nmap/restore). Tambahan opsional: CSRF token, rate-limit login, UI info user lengkap di dashboard. -->
