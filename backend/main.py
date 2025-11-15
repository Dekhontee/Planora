from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import io
import pdfplumber
import json
from backend.parser import extract_topics, generate_plan
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import sqlite3
import os
from datetime import datetime, timedelta
# Optional encryption for token-at-rest
try:
    from cryptography.fernet import Fernet, InvalidToken
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

app = FastAPI(title="Planora Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/plan")
async def create_plan(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    syllabus_text: Optional[str] = Form(None),
    topics_text: Optional[str] = Form(None),
    exam_date: Optional[str] = Form(None),
    exam_type: Optional[str] = Form("final"),
    hours_per_day: float = Form(2.0),
    plan_length: int = Form(14),
    review_day_fraction: Optional[float] = Form(None),
    course_type: str = Form("General"),
    use_ocr_gpu: Optional[str] = Form(None),
):
    """Create a study plan from an uploaded syllabus (PDF), pasted text, manual topics, or image OCR."""
    # Priority: manual topics_text -> image OCR -> uploaded file (pdf/text) -> syllabus_text
    text = ""

    if topics_text:
        # User provided topic list manually (one per line or comma separated)
        text = topics_text
    elif image is not None:
        contents = await image.read()
        try:
            # try OCR from image
            from .parser import extract_text_from_image
            use_gpu_flag = False
            if use_ocr_gpu and str(use_ocr_gpu).lower() in ("1","true","yes"):
                use_gpu_flag = True

            ocr_text = extract_text_from_image(contents, use_gpu=use_gpu_flag)
            text = ocr_text or ""
        except Exception:
            text = ""
    elif file is not None:
        contents = await file.read()
        # If image file uploaded via file field
        if file.content_type and file.content_type.startswith("image"):
            try:
                from .parser import extract_text_from_image
                use_gpu_flag = False
                if use_ocr_gpu and str(use_ocr_gpu).lower() in ("1","true","yes"):
                    use_gpu_flag = True
                text = extract_text_from_image(contents, use_gpu=use_gpu_flag) or ""
            except Exception:
                text = ""
        else:
            try:
                with pdfplumber.open(io.BytesIO(contents)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                    text = "\n\n".join(pages)
            except Exception:
                try:
                    text = contents.decode("utf-8")
                except Exception:
                    text = ""

    if not text and syllabus_text:
        text = syllabus_text

    if not text:
        return {"error": "No syllabus, topics, or image provided"}

    topics = extract_topics(text)
    # Pass optional review_day_fraction through to generator
    try:
        rfrac = float(review_day_fraction) if review_day_fraction is not None else None
    except Exception:
        rfrac = None
    plan = generate_plan(topics, plan_length=plan_length, hours_per_day=hours_per_day, exam_type=exam_type, review_day_fraction=rfrac)

    response = {
        "exam_date": exam_date,
        "exam_type": exam_type,
        "plan_length": plan_length,
        "hours_per_day": hours_per_day,
        "course_type": course_type,
        "topics_count": len(topics),
        "plan": plan,
    }
    return response


DB_PATH = os.path.join(os.path.dirname(__file__), 'plans.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        course_type TEXT,
        exam_date TEXT,
        plan_json TEXT
    )''')
    # Table for storing OAuth tokens (refresh tokens) tied to a plan or user
    c.execute('''CREATE TABLE IF NOT EXISTS oauth_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER,
        refresh_token TEXT,
        access_token TEXT,
        scope TEXT,
        expires_at TEXT,
        created_at TEXT
    )''')
    # Users table for simple account management
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )''')

    # Ensure optional user_id columns exist on plans and oauth_tokens (for migrations)
    # SQLite: add column if not exists by checking pragma
    def _ensure_column(table, column_def):
        colname = column_def.split()[0]
        c.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in c.fetchall()]
        if colname not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")

    _ensure_column('plans', 'user_id INTEGER')
    _ensure_column('oauth_tokens', 'user_id INTEGER')
    conn.commit()
    conn.close()


init_db()


@app.post('/save_plan')
async def save_plan(plan: str = Form(...), course_type: str = Form(None), exam_date: str = Form(None), user_id: Optional[int] = Form(None)):
    """Save a plan JSON and return an id."""
    # Accept optional user_id to associate the plan
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    if user_id:
        c.execute('INSERT INTO plans (created_at, course_type, exam_date, plan_json, user_id) VALUES (?,?,?,?,?)', (now, course_type, exam_date, plan, user_id))
    else:
        c.execute('INSERT INTO plans (created_at, course_type, exam_date, plan_json) VALUES (?,?,?,?)', (now, course_type, exam_date, plan))
    plan_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": plan_id}


@app.get('/list_plans')
async def list_plans(limit: int = 50, user_id: Optional[int] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute('SELECT id, created_at, course_type, exam_date, user_id FROM plans WHERE user_id=? ORDER BY id DESC LIMIT ?', (user_id, limit))
    else:
        c.execute('SELECT id, created_at, course_type, exam_date, user_id FROM plans ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    items = []
    for r in rows:
        items.append({"id": r[0], "created_at": r[1], "course_type": r[2], "exam_date": r[3], "user_id": r[4]})
    return {"plans": items}


@app.post('/register')
async def register(username: str = Form(...), password: str = Form(...)):
    """Register a new user. Returns user id on success or error if username exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    # check exists
    c.execute('SELECT id FROM users WHERE username=?', (username,))
    if c.fetchone():
        conn.close()
        return {"error": "username_exists"}
    ph = _hash_password(password)
    c.execute('INSERT INTO users (username, password_hash, created_at) VALUES (?,?,?)', (username, ph, now))
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return {"user_id": uid}


@app.post('/login')
async def login(username: str = Form(...), password: str = Form(...)):
    """Simple login: verify password and return user_id on success."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"error": "not_found"}
    uid, stored = row
    if not _verify_password(stored, password):
        return {"error": "invalid_credentials"}
    return {"user_id": uid}


@app.post('/update_plan')
async def update_plan(id: int = Form(...), plan: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE plans SET plan_json=? WHERE id=?', (plan, id))
    conn.commit()
    conn.close()
    return {"ok": True}


def _get_oauth_client_creds():
    # Read Google OAuth client id/secret from env vars
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    return client_id, client_secret


def _get_cipher():
    """Return a Fernet cipher if ENCRYPTION_KEY env var is set and cryptography is available.

    The `ENCRYPTION_KEY` should be a URL-safe base64-encoded 32-byte key as produced by
    `Fernet.generate_key()`. If not set or cryptography not installed, returns None.
    """
    # Support multiple keys for rotation: ENCRYPTION_KEYS (comma-separated)
    if not CRYPTO_AVAILABLE:
        return None
    keys = os.environ.get('ENCRYPTION_KEYS') or os.environ.get('ENCRYPTION_KEY')
    if not keys:
        return None
    # return list of ciphers (primary first)
    key_list = [k.strip() for k in keys.split(',') if k.strip()]
    ciphers = []
    for k in key_list:
        try:
            ciphers.append(Fernet(k.encode() if isinstance(k, str) else k))
        except Exception:
            continue
    if not ciphers:
        return None
    return ciphers


def _encrypt_token(plain: Optional[str]) -> Optional[str]:
    if not plain:
        return plain
    ciphers = _get_cipher()
    if not ciphers:
        return plain
    # use primary cipher (first)
    try:
        return ciphers[0].encrypt(plain.encode()).decode()
    except Exception:
        return plain


def _decrypt_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return token
    ciphers = _get_cipher()
    if not ciphers:
        return token
    # try each cipher (supports rotation)
    for c in ciphers:
        try:
            return c.decrypt(token.encode()).decode()
        except Exception:
            continue
    return None


# Simple password hashing utilities (PBKDF2)
import hashlib, binascii

def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    if not salt:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return binascii.hexlify(salt).decode() + "$" + binascii.hexlify(dk).decode()

def _verify_password(stored: str, supplied: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split('$')
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac('sha256', supplied.encode(), salt, 100_000)
        return binascii.hexlify(dk).decode() == dk_hex
    except Exception:
        return False


@app.get('/gcal_auth_start')
async def gcal_auth_start(plan_id: Optional[int] = None, user_id: Optional[int] = None):
    """Return a Google OAuth2 authorization URL. Set env vars GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.

    The `state` param will include the plan_id (if provided) so the callback can store tokens for that plan.
    """
    client_id, client_secret = _get_oauth_client_creds()
    if not client_id:
        return {"error": "GOOGLE_CLIENT_ID not configured in server environment"}
    redirect_uri = f"http://localhost:8000/gcal_oauth_callback"
    scope = "https://www.googleapis.com/auth/calendar.events"
    state_items = []
    if plan_id:
        state_items.append(f"plan_id:{plan_id}")
    if user_id:
        state_items.append(f"user_id:{user_id}")
    state = ";".join(state_items)
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
        "&access_type=offline&prompt=consent&include_granted_scopes=true"
    )
    if state:
        auth_url += f"&state={state}"
    return {"auth_url": auth_url}


@app.get('/gcal_oauth_callback')
async def gcal_oauth_callback(code: Optional[str] = None, state: Optional[str] = None):
    """Exchange code for tokens and store refresh_token in DB. Redirects to a simple success page.

    Note: This endpoint is meant for local testing. In production, secure storage and HTTPS required.
    """
    client_id, client_secret = _get_oauth_client_creds()
    if not client_id or not client_secret:
        return {"error": "OAuth client credentials not configured on server"}
    if not code:
        return {"error": "missing code"}
    import requests as _requests
    token_resp = _requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': f'http://localhost:8000/gcal_oauth_callback',
        'grant_type': 'authorization_code'
    })
    if token_resp.status_code != 200:
        return {"error": "token exchange failed", "details": token_resp.text}
    toks = token_resp.json()
    refresh_token = toks.get('refresh_token')
    access_token = toks.get('access_token')
    expires_in = toks.get('expires_in')
    scope = toks.get('scope')
    expires_at = None
    if expires_in:
        expires_at = (datetime.utcnow() + timedelta(seconds=int(expires_in))).isoformat()

    # extract plan_id and user_id from state if present (state format: 'plan_id:123;user_id:45')
    plan_id = None
    user_id = None
    if state:
        parts = [p for p in state.split(';') if p]
        for p in parts:
            if p.startswith('plan_id:'):
                try:
                    plan_id = int(p.split(':',1)[1])
                except Exception:
                    plan_id = None
            if p.startswith('user_id:'):
                try:
                    user_id = int(p.split(':',1)[1])
                except Exception:
                    user_id = None

    # store tokens (encrypt refresh token if possible)
    enc_refresh = _encrypt_token(refresh_token)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO oauth_tokens (plan_id, refresh_token, access_token, scope, expires_at, created_at, user_id) VALUES (?,?,?,?,?,?,?)', (plan_id, enc_refresh, access_token, scope, expires_at, now, user_id))
    conn.commit()
    conn.close()

    # Return a small HTML success page that instructs the user
    html = """
    <html>
      <body>
        <h3>Google Calendar connected</h3>
        <p>You can now return to the Planora app. The server stored your refresh token for creating calendar events.</p>
      </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


def _refresh_access_token(refresh_token: str):
    client_id, client_secret = _get_oauth_client_creds()
    if not client_id or not client_secret:
        return None
    import requests as _requests
    resp = _requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    })
    if resp.status_code != 200:
        return None
    return resp.json()


@app.get('/get_plan')
async def get_plan(id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT plan_json FROM plans WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"error": "not found"}
    try:
        return json.loads(row[0])
    except Exception:
        return {"plan": row[0]}


@app.post('/gcal_create')
async def gcal_create(events: str = Form(...), access_token: str = Form(...)):
    """Create events on Google Calendar using a provided OAuth access token.

    `events` should be a JSON string list of {summary, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)}
    The endpoint uses the Google Calendar REST API and requires a valid user access token.
    """
    import requests as _requests
    try:
        evs = json.loads(events)
    except Exception:
        return {"error": "invalid events payload"}
    # If access_token looks like 'plan:<id>' then use stored refresh token for that plan
    created = []
    if access_token.startswith('plan:'):
        try:
            pid = int(access_token.split(':',1)[1])
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT refresh_token FROM oauth_tokens WHERE plan_id=? ORDER BY id DESC LIMIT 1', (pid,))
            row = c.fetchone()
            conn.close()
            if not row:
                return {"error": "no refresh token for plan"}
            stored = row[0]
            # decrypt stored refresh token if encrypted
            refresh_token = _decrypt_token(stored) or stored
            tok = _refresh_access_token(refresh_token)
            if not tok:
                return {"error": "failed to refresh access token"}
            token_to_use = tok.get('access_token')
        except Exception as e:
            return {"error": f"failed to use plan token: {e}"}
    else:
        token_to_use = access_token

    headers = {"Authorization": f"Bearer {token_to_use}", "Content-Type": "application/json"}
    for e in evs:
        body = {
            "summary": e.get('summary'),
            "start": {"date": e.get('start_date')},
            "end": {"date": e.get('end_date')},
        }
        r = _requests.post('https://www.googleapis.com/calendar/v3/calendars/primary/events', headers=headers, json=body)
        if r.status_code in (200,201):
            created.append(r.json())
        else:
            created.append({"error": r.text, "status": r.status_code})
    return {"created": created}


@app.post('/gcal_revoke')
async def gcal_revoke(plan_id: Optional[int] = Form(None), user_id: Optional[int] = Form(None)):
    """Revoke Google tokens for a plan or user. Calls Google's token revocation endpoint and marks tokens revoked.

    Returns a summary of revocation attempts.
    """
    import requests as _requests
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if plan_id:
        c.execute('SELECT id, refresh_token FROM oauth_tokens WHERE plan_id=? AND revoked=0', (plan_id,))
    elif user_id:
        c.execute('SELECT id, refresh_token FROM oauth_tokens WHERE user_id=? AND revoked=0', (user_id,))
    else:
        conn.close()
        return {"error": "provide plan_id or user_id"}
    rows = c.fetchall()
    results = []
    for r in rows:
        oid, stored = r
        # attempt decrypt, fallback to plaintext
        refresh_token = _decrypt_token(stored) or stored
        if not refresh_token:
            results.append({"id": oid, "status": "no_token"})
            continue
        try:
            resp = _requests.post('https://oauth2.googleapis.com/revoke', params={'token': refresh_token}, headers={'content-type': 'application/x-www-form-urlencoded'})
            status = resp.status_code
            ok = status in (200, 400)  # 200 OK, 400 if token already invalid per Google
            if ok:
                c.execute('UPDATE oauth_tokens SET revoked=1 WHERE id=?', (oid,))
                results.append({"id": oid, "status": "revoked", "code": status})
            else:
                results.append({"id": oid, "status": "failed", "code": status, "body": resp.text})
        except Exception as e:
            results.append({"id": oid, "status": "error", "error": str(e)})
    conn.commit()
    conn.close()
    return {"results": results}


@app.post('/rotate_keys')
async def rotate_keys(new_key: str = Form(...), backup: bool = Form(False)):
    """Rotate encryption keys for stored refresh tokens.

    This endpoint will decrypt each stored refresh token using existing keys (or treat as plaintext)
    and re-encrypt using `new_key`. If `backup` is true, the previous ciphertext is stored in
    `refresh_token_backup` column.

    Warning: rotating keys is a sensitive operation; ensure you keep `new_key` secure.
    """
    if not CRYPTO_AVAILABLE:
        return {"error": "cryptography not available on server"}
    try:
        new_cipher = Fernet(new_key.encode() if isinstance(new_key, str) else new_key)
    except Exception as e:
        return {"error": f"invalid new_key: {e}"}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # ensure backup column exists
    c.execute("PRAGMA table_info(oauth_tokens)")
    cols = [r[1] for r in c.fetchall()]
    if 'refresh_token_backup' not in cols:
        c.execute('ALTER TABLE oauth_tokens ADD COLUMN refresh_token_backup TEXT')

    c.execute('SELECT id, refresh_token FROM oauth_tokens')
    rows = c.fetchall()
    rotated = 0
    failed = []
    for r in rows:
        oid, stored = r
        # attempt to decrypt with existing keys; if fails, assume stored plaintext
        try:
            plain = _decrypt_token(stored)
            if plain is None:
                # treat stored as plaintext
                plain = stored
        except Exception:
            plain = stored
        if not plain:
            failed.append({"id": oid, "error": "no_plaintext"})
            continue
        try:
            new_ciphertext = new_cipher.encrypt(plain.encode()).decode()
            if backup:
                c.execute('UPDATE oauth_tokens SET refresh_token_backup=? WHERE id=?', (stored, oid))
            c.execute('UPDATE oauth_tokens SET refresh_token=? WHERE id=?', (new_ciphertext, oid))
            rotated += 1
        except Exception as e:
            failed.append({"id": oid, "error": str(e)})
    conn.commit()
    conn.close()
    return {"rotated": rotated, "failed": failed}


@app.post('/export_pdf')
async def export_pdf(plan: dict = Form(...)):
    """Accepts a `plan` JSON (as form field or string) and returns a simple PDF representation."""
    # `plan` may arrive as a JSON string
    import json as _json
    try:
        if isinstance(plan, str):
            plan_obj = _json.loads(plan)
        else:
            plan_obj = plan
    except Exception:
        plan_obj = plan

    # Create PDF in a temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    c = canvas.Canvas(tmp.name, pagesize=letter)
    width, height = letter
    x = 40
    y = height - 40
    line_height = 14

    title = f"Planora Study Plan — {plan_obj.get('plan_length', '')} days"
    c.setFont('Helvetica-Bold', 16)
    c.drawString(x, y, title)
    y -= 30

    c.setFont('Helvetica', 10)
    c.drawString(x, y, f"Course: {plan_obj.get('course_type','')}")
    y -= 16
    c.drawString(x, y, f"Exam Date: {plan_obj.get('exam_date','')}")
    y -= 20

    for day in plan_obj.get('plan', []):
        if y < 80:
            c.showPage()
            y = height - 40
            c.setFont('Helvetica', 10)
        header = f"Day {day.get('day')}{' (Review)' if day.get('is_review') else ''} — {day.get('total_minutes',0)} minutes"
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x, y, header)
        y -= 16
        c.setFont('Helvetica', 10)
        c.drawString(x+8, y, day.get('daily_summary',''))
        y -= 14
        for t in day.get('topics', []):
            text = f"- {t.get('title')} ({t.get('estimated_minutes')} min)"
            c.drawString(x+12, y, text)
            y -= line_height
        y -= 8

    c.save()
    tmp.flush()
    tmp.seek(0)

    return StreamingResponse(open(tmp.name, 'rb'), media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=planora_plan.pdf"})


@app.get('/ocr_status')
async def ocr_status():
    """Return OCR availability info: pytesseract, tesseract binary, easyocr."""
    info = {
        'pytesseract_installed': False,
        'tesseract_binary': False,
        'easyocr_installed': False,
    }
    try:
        import pytesseract
        info['pytesseract_installed'] = True
        # check binary presence
        import shutil
        info['tesseract_binary'] = bool(shutil.which('tesseract'))
    except Exception:
        pass
    try:
        import easyocr
        info['easyocr_installed'] = True
    except Exception:
        pass
    return info

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
