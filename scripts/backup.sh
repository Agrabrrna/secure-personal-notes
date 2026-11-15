#!/usr/bin/env bash
set -euo pipefail
# SEC-07: encrypted SQLite backup (run via cron on Ubuntu VM)
APP_DIR="${APP_DIR:-/opt/secure-personal-notes}"
DB="${DB:-$APP_DIR/instance/app.db}"
OUT_DIR="${OUT_DIR:-$APP_DIR/backups}"
PASSPHRASE_FILE="${PASSPHRASE_FILE:-$APP_DIR/config/backup.pass}" # chmod 600, outside git
mkdir -p "$OUT_DIR"
STAMP=$(date +%F_%H%M%S)
OUT="$OUT_DIR/app_$STAMP.db.gpg"
gpg --batch --yes --passphrase-file "$PASSPHRASE_FILE" --symmetric --cipher-algo AES256 -o "$OUT" "$DB"
chmod 600 "$OUT"
# retention: keep 14 days (Q5 adjustable)
find "$OUT_DIR" -name 'app_*.db.gpg' -mtime +14 -delete
echo "backup: $OUT"
# restore example:
# gpg --batch --passphrase-file $PASSPHRASE_FILE -o instance/app.db -d backups/app_<STAMP>.db.gpg
