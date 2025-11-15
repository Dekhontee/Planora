#!/usr/bin/env bash
# Wrapper for admin_rotate_keys.py
# Usage: ./scripts/admin_rotate_keys.sh <new_key_base64> [--backup]
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <new_fernet_key_base64> [--backup]"
  exit 2
fi
NEW_KEY="$1"
shift
BACKUP_ARG=""
DRY_RUN_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup) BACKUP_ARG="--backup"; shift ;;
    --dry-run) DRY_RUN_ARG="--dry-run"; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done
python3 scripts/admin_rotate_keys.py --new-key "$NEW_KEY" --db backend/plans.db $BACKUP_ARG $DRY_RUN_ARG
