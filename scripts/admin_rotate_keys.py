#!/usr/bin/env python3
"""Admin key rotation script for Planora

Usage:
  ./scripts/admin_rotate_keys.py --new-key <new_fernet_key_base64> [--db /path/to/plans.db] [--backup]

This script will read existing keys from the environment variable `ENCRYPTION_KEYS` (comma-separated),
try to decrypt each stored `refresh_token` from the `oauth_tokens` table using those keys,
and re-encrypt using the provided `--new-key`. If `--backup` is set, the previous ciphertext is written
into `refresh_token_backup` column.

Security: run this script on the server where DB and keys reside. Do NOT transmit keys over network.
"""

import argparse
import os
import sqlite3
import sys
from typing import List

try:
    from cryptography.fernet import Fernet
except Exception:
    print("cryptography package is required. Install with: pip install cryptography", file=sys.stderr)
    sys.exit(2)


def load_ciphers_from_env() -> List[Fernet]:
    keys = os.environ.get('ENCRYPTION_KEYS') or os.environ.get('ENCRYPTION_KEY')
    if not keys:
        return []
    key_list = [k.strip() for k in keys.split(',') if k.strip()]
    ciphers = []
    for k in key_list:
        try:
            ciphers.append(Fernet(k.encode() if isinstance(k, str) else k))
        except Exception:
            print(f"Warning: skipping invalid key in ENCRYPTION_KEYS: {k}")
    return ciphers


def try_decrypt(token: str, ciphers: List[Fernet]) -> str | None:
    if not token:
        return None
    # try each cipher
    for c in ciphers:
        try:
            return c.decrypt(token.encode()).decode()
        except Exception:
            continue
    # nothing worked
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--new-key', required=True, help='New Fernet key (base64) to encrypt tokens with')
    p.add_argument('--db', default='backend/plans.db', help='Path to sqlite DB')
    p.add_argument('--backup', action='store_true', help='Backup existing ciphertext in refresh_token_backup')
    p.add_argument('--dry-run', action='store_true', help='Do not write changes, just preview')
    args = p.parse_args()

    new_key = args.new_key
    try:
        new_cipher = Fernet(new_key.encode() if isinstance(new_key, str) else new_key)
    except Exception as e:
        print(f"Invalid new_key: {e}", file=sys.stderr)
        sys.exit(2)

    ciphers = load_ciphers_from_env()
    if not ciphers:
        print("No existing ENCRYPTION_KEYS found in env; assuming tokens may be plaintext.", file=sys.stderr)

    db_path = args.db
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}", file=sys.stderr)
        sys.exit(2)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # ensure columns exist
    cur.execute("PRAGMA table_info(oauth_tokens)")
    cols = [r[1] for r in cur.fetchall()]
    if 'refresh_token_backup' not in cols:
        if args.backup:
            cur.execute('ALTER TABLE oauth_tokens ADD COLUMN refresh_token_backup TEXT')
    if 'revoked' not in cols:
        cur.execute('ALTER TABLE oauth_tokens ADD COLUMN revoked INTEGER DEFAULT 0')

    cur.execute('SELECT id, refresh_token FROM oauth_tokens')
    rows = cur.fetchall()
    total = len(rows)
    rotated = 0
    failed = []

    for oid, stored in rows:
        stored = stored or ''
        plain = None
        if ciphers:
            plain = try_decrypt(stored, ciphers)
        if plain is None:
            # treat as plaintext if not decryptable
            plain = stored
        if not plain:
            failed.append({'id': oid, 'reason': 'no_plaintext'})
            continue
        try:
            new_ct = new_cipher.encrypt(plain.encode()).decode()
            if args.dry_run:
                print(f"[DRY] would update id={oid}")
                rotated += 1
                continue
            if args.backup:
                cur.execute('UPDATE oauth_tokens SET refresh_token_backup=? WHERE id=?', (stored, oid))
            cur.execute('UPDATE oauth_tokens SET refresh_token=? WHERE id=?', (new_ct, oid))
            rotated += 1
        except Exception as e:
            failed.append({'id': oid, 'error': str(e)})

    if not args.dry_run:
        conn.commit()
    conn.close()

    print(f"Processed {total} rows: rotated={rotated}, failed={len(failed)}")
    if failed:
        print("Failures:")
        for f in failed:
            print(f)


if __name__ == '__main__':
    main()
