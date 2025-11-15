# Planora Project File Structure Reference

This document provides a visual overview of the complete Planora project structure.

---

## Complete Directory Tree

```
Planora/
│
├── 📄 README.md                          # Main project README
├── 📄 QUICKSTART.md                      # ⭐ Start here! 5-phase quick setup
├── 📄 FRONTEND_SETUP.md                  # Complete setup & deployment guide
├── 📄 TROUBLESHOOTING.md                 # Troubleshooting for all components
├── 📄 REACT_FRONTEND_COMPLETE.md         # This file - completion summary
├── 📄 .env.example                       # Backend environment variables template
├── 📄 requirements.txt                   # Python dependencies
├── 📄 LICENSE
├── 📄 sample_syllabus.txt                # Example syllabus for testing
├── 📄 run_backend.sh                     # Quick start: run backend
├── 📄 run_frontend.sh                    # Quick start: run Streamlit
├── 📄 demo_backend.sh                    # Demo: test backend API
│
├── 📁 backend/                           # FastAPI backend
│   ├── __init__.py
│   ├── main.py                           # All API endpoints
│   ├── parser.py                         # Syllabus parsing & plan generation
│   ├── ml_models.py                      # Optional ML models
│   ├── plans.db                          # SQLite database (created on first run)
│   └── __pycache__/                      # Python cache (ignored)
│
├── 📁 frontend/                          # ✨ React + Vite Frontend (NEW!)
│   │
│   ├── 📄 package.json                   # NPM dependencies & scripts
│   ├── 📄 package-lock.json              # Lock file (created after npm install)
│   ├── 📄 vite.config.ts                 # Vite build & dev server config
│   ├── 📄 tsconfig.json                  # TypeScript configuration
│   ├── 📄 tsconfig.node.json             # TypeScript for build tools
│   ├── 📄 tailwind.config.js             # Tailwind CSS theme
│   ├── 📄 postcss.config.js              # PostCSS (for Tailwind)
│   ├── 📄 vercel.json                    # Vercel deployment config
│   ├── 📄 .env.example                   # Environment variables template
│   ├── 📄 .gitignore                     # Git ignore patterns
│   ├── 📄 README.md                      # Frontend-specific README
│   │
│   ├── 📁 src/                           # Source code
│   │   ├── 📄 main.tsx                   # React app entry point
│   │   ├── 📄 App.tsx                    # Main app component
│   │   ├── 📄 index.css                  # Global Tailwind styles
│   │   │
│   │   ├── 📁 components/                # React components
│   │   │   ├── 📄 PlanForm.tsx           # Study plan form
│   │   │   ├── 📄 PlanDisplay.tsx        # Plan display & controls
│   │   │   │
│   │   │   └── 📁 ui/                    # Reusable UI components
│   │   │       ├── 📄 button.tsx         # Button component
│   │   │       ├── 📄 card.tsx           # Card component
│   │   │       ├── 📄 input.tsx          # Input component
│   │   │       ├── 📄 textarea.tsx       # Textarea component
│   │   │       └── 📄 checkbox.tsx       # Checkbox component
│   │   │
│   │   └── 📁 lib/                       # Utilities & API client
│   │       ├── 📄 api.ts                 # Axios API client (all endpoints)
│   │       └── 📄 utils.ts               # Helper functions (cn, etc.)
│   │
│   ├── 📁 node_modules/                  # NPM packages (created after npm install)
│   ├── 📁 dist/                          # Production build (created after npm build)
│   └── 📁 .vscode/                       # VSCode settings (optional)
│
├── 📁 streamlit_app.py                   # Legacy Streamlit frontend (optional)
│
├── 📁 scripts/                           # Utility scripts
│   ├── 📄 admin_rotate_keys.py           # Admin: rotate encryption keys
│   └── 📄 admin_rotate_keys.sh           # Shell wrapper
│
├── 📁 deploy/                            # Deployment configs
│   ├── 📄 README.md
│   ├── 📄 planora-backend.service        # systemd service file
│   ├── 📄 planora-frontend.service       # systemd service file (legacy)
│   └── 📄 supervisor.conf                # Supervisor process config
│
├── 📁 tests/                             # Unit tests
│   ├── 📄 test_api.py                    # API tests (pytest)
│   └── 📄 __pycache__/
│
└── 📁 images/                            # Project images (if any)
```

---

## Key Files Explained

### Configuration Files

| File | Purpose | Edit? |
|------|---------|-------|
| `package.json` | Dependencies, scripts, metadata | ✏️ Add packages |
| `vite.config.ts` | Vite build config, React plugin, proxy | ⚠️ Advanced |
| `tailwind.config.js` | Tailwind theme, content paths | ✏️ Customize colors |
| `tsconfig.json` | TypeScript compiler settings | ⚠️ Usually not |
| `vercel.json` | Vercel deployment settings | ✏️ Environment vars |

### Backend Entry Points

| File | Purpose |
|------|---------|
| `backend/main.py` | All API endpoints (plan, auth, export, etc.) |
| `backend/parser.py` | Syllabus parsing & plan generation logic |
| `backend/plans.db` | SQLite database (auto-created) |

### Frontend Entry Points

| File | Purpose |
|------|---------|
| `frontend/src/main.tsx` | React app root (ReactDOM.createRoot) |
| `frontend/src/App.tsx` | Main app component layout |
| `frontend/src/components/PlanForm.tsx` | Study plan form component |
| `frontend/src/components/PlanDisplay.tsx` | Plan display & controls |

---

## Important Files You Should Know About

### 🎯 Start Here (First Time Setup)
1. Read [`QUICKSTART.md`](./QUICKSTART.md) — 5-phase checklist
2. Read [`frontend/README.md`](./frontend/README.md) — Frontend-specific info
3. Run `cd frontend && npm install && npm run dev`

### 📚 Reference Guides
- [`README.md`](./README.md) — Project overview
- [`FRONTEND_SETUP.md`](./FRONTEND_SETUP.md) — Complete setup & deployment
- [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) — Common issues

### 🔧 Configuration
- `.env.example` — Backend env vars template
- `frontend/.env.example` — Frontend env vars template
- `frontend/vite.config.ts` — Dev server & proxy config

### 🚀 Deployment
- `frontend/vercel.json` — Vercel settings
- `deploy/planora-backend.service` — systemd service
- `deploy/supervisor.conf` — Supervisor process manager

---

## Development Workflow

### Terminal 1: Backend
```bash
cd /workspaces/Planora
python3 -m venv venv  # Optional: virtual environment
source venv/bin/activate  # Activate venv
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd /workspaces/Planora/frontend
npm install  # First time only
npm run dev
# Open http://localhost:5173
```

### Testing
```bash
cd /workspaces/Planora
pytest tests/test_api.py -v
```

---

## File Statistics

| Category | Count | Total Lines |
|----------|-------|------------|
| Backend Python | 4 | ~2,000 |
| Frontend React/TS | 14 | ~1,500 |
| Configuration | 8 | ~500 |
| Documentation | 5 | ~2,000 |
| **Total** | **~31** | **~6,000** |

---

## Build Outputs

### Frontend Production Build
```bash
npm run build
# Output: frontend/dist/
#   ├── index.html          # Main HTML file
#   ├── assets/
#   │   ├── index-xxx.js    # Minified JavaScript
#   │   ├── index-xxx.css   # Minified CSS
#   │   └── vendor-xxx.js   # Third-party code (React, etc.)
#   └── vite.svg            # Vite logo asset
```

### Backend Database
```
backend/plans.db  # SQLite database
  ├── users table (id, email, password_hash)
  ├── plans table (id, user_id, plan_json, created_at)
  └── oauth_tokens table (user_id, encrypted_refresh_token)
```

---

## Dependencies Overview

### Backend (Python)
```
fastapi              # Web framework
uvicorn              # ASGI server
pdfplumber          # PDF parsing
pytesseract         # OCR
easyocr             # Alternative OCR
sqlalchemy          # Database ORM
cryptography        # Token encryption
```

### Frontend (JavaScript/TypeScript)
```
react               # UI library
react-dom           # React DOM rendering
vite                # Build tool
typescript          # Type safety
tailwindcss         # CSS framework
@radix-ui/*         # Accessible components
axios               # HTTP client
lucide-react        # Icons
```

---

## Command Reference

### Backend Commands
```bash
# Start backend
uvicorn backend.main:app --reload

# Run tests
pytest tests/ -v

# Check API docs (when running)
curl http://localhost:8000/docs

# Rotate encryption keys
python3 scripts/admin_rotate_keys.py
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Format code (if configured)
npm run lint
```

---

## Environment Variables

### Backend (`.env`)
```
DATABASE_URL=sqlite:///./backend/plans.db
ENCRYPTION_KEYS=key1,key2,key3
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

### Frontend (`.env.local`)
```
VITE_API_URL=http://localhost:8000
```

---

## Next Steps

1. ✅ Review this file structure
2. ✅ Open `frontend/` directory
3. ✅ Run `npm install`
4. ✅ Run `npm run dev`
5. ✅ Open http://localhost:5173
6. ✅ Test the app end-to-end

See [`QUICKSTART.md`](./QUICKSTART.md) for deployment instructions.

---

*Happy coding! 🚀*
