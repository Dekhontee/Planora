Planora deploy helpers

This folder contains example service configs and an admin key rotation script.

Systemd services
----------------
Two example unit files are provided:
- `planora-backend.service` — runs the FastAPI backend using Uvicorn
- `planora-frontend.service` — runs the Streamlit frontend

These are templates. Before enabling, adjust `ExecStart` to point to your Python virtualenv, and choose an appropriate `User`/`Group`.

Example enable + start (as root):

```bash
cp deploy/planora-backend.service /etc/systemd/system/
cp deploy/planora-frontend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable planora-backend.service
systemctl enable planora-frontend.service
systemctl start planora-backend.service
systemctl start planora-frontend.service
```

Supervisor config
-----------------
A `supervisor` program block is provided in `deploy/supervisor.conf`. Drop this into your Supervisor directory (commonly `/etc/supervisor/conf.d/`) and run `supervisorctl reread && supervisorctl update`.

Admin key rotation script
-------------------------
- `scripts/admin_rotate_keys.py`: Python script that rotates encryption keys locally against the SQLite DB (`backend/plans.db`).
- `scripts/admin_rotate_keys.sh`: small wrapper for convenience.

Usage example (safe local run):

```bash
# generate new key
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY

# set ENCRYPTION_KEYS to existing keys (if any) in the environment, then run rotation
export ENCRYPTION_KEYS="OLD_KEY_BASE64"
./scripts/admin_rotate_keys.sh NEW_KEY_BASE64 --backup

# dry-run preview
./scripts/admin_rotate_keys.sh NEW_KEY_BASE64 --dry-run
```

Security notes
--------------
- Do NOT transmit encryption keys over insecure networks. Run the rotation script on the host that contains the DB and keys.
- For production, store keys in a secure vault and use short-lived credentials or KMS.

