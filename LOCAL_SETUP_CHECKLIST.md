# Developer's Local Setup Checklist

Complete this checklist to get Planora running on your machine.

---

## ✅ Prerequisites (5 minutes)

- [ ] **Python 3.11+**
  - Test: `python3 --version`
  - Download: https://www.python.org/downloads/

- [ ] **Node.js 18+**
  - Test: `node --version && npm --version`
  - Download: https://nodejs.org

- [ ] **Git** (optional but recommended)
  - Test: `git --version`
  - Download: https://git-scm.com

---

## ✅ Step 1: Backend Setup (3 minutes)

Navigate to project root:
```bash
cd /workspaces/Planora
```

- [ ] Create Python virtual environment (optional but recommended):
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

- [ ] Install Python dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  Expected output: `Successfully installed fastapi uvicorn pdfplumber ...`

- [ ] Verify installation:
  ```bash
  python3 -c "import fastapi; print('FastAPI installed')"
  ```

---

## ✅ Step 2: Backend - Start Server (2 minutes)

**In Terminal 1:**
```bash
cd /workspaces/Planora
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

- [ ] Backend is running ✓
- [ ] Test it works:
  ```bash
  # In another terminal
  curl http://localhost:8000/docs
  ```

---

## ✅ Step 3: Frontend Setup (5 minutes)

Navigate to frontend:
```bash
cd /workspaces/Planora/frontend
```

- [ ] Install Node dependencies:
  ```bash
  npm install
  ```
  Expected output: `added 200+ packages in 20–60 seconds`

- [ ] Verify Vite is installed:
  ```bash
  npm list vite
  ```

---

## ✅ Step 4: Frontend - Start Dev Server (2 minutes)

**In Terminal 2:**
```bash
cd /workspaces/Planora/frontend
npm run dev
```

Expected output:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

- [ ] Frontend is running ✓
- [ ] Open browser: http://localhost:5173
- [ ] Page loads successfully ✓

---

## ✅ Step 5: Test End-to-End (5 minutes)

In your browser at http://localhost:5173:

- [ ] **Register**
  - Enter email: `test@example.com`
  - Enter password: `TestPassword123`
  - Click "Register"
  - Should see success message

- [ ] **Login**
  - Email: `test@example.com`
  - Password: `TestPassword123`
  - Click "Login"
  - Should see plan form

- [ ] **Generate a Plan**
  - **Topics**: Paste or type:
    ```
    Chapter 1: Basics
    Chapter 2: Advanced Concepts
    Chapter 3: Applications
    ```
  - **Exam Date**: Pick a date 14 days from today
  - **Hours per Day**: `2`
  - **Plan Length**: `14 days`
  - **Review Days**: `8%` (default)
  - Click **"Generate Plan"**

- [ ] **View Generated Plan**
  - Should see metrics (total days, hours/day, topics, review days)
  - Should see day cards with topics and times
  - Should see checkboxes for each day

- [ ] **Save Plan**
  - Check a few days as "done"
  - Click **"Save Plan"**
  - Should see success message

- [ ] **Export Plan**
  - Click **"Export as JSON"** - should download file
  - Click **"Export as ICS"** - should download calendar file
  - Click **"Export as PDF"** - should download PDF

---

## ✅ Step 6: Verify Logs (2 minutes)

**Backend Terminal (Terminal 1):**
- [ ] Should see requests logged:
  ```
  INFO:     127.0.0.1:xxxxx - "POST /plan HTTP/1.1" 200 OK
  INFO:     127.0.0.1:xxxxx - "GET /api/plan HTTP/1.1" 200 OK
  ```

**Frontend Terminal (Terminal 2):**
- [ ] Should see module reloads (when you edit files):
  ```
  [vite] hmr update /src/App.tsx
  ```

---

## ✅ Step 7: Test File Changes (2 minutes)

- [ ] Edit `frontend/src/App.tsx` - change title text
  - Save file
  - Browser should auto-refresh
  - Change should appear immediately ✓

- [ ] Edit `frontend/src/index.css` - change a color
  - Save file
  - Browser should auto-refresh
  - Change should appear immediately ✓

---

## ✅ Optional: Test Specific Features

### Test PDF Upload
```bash
# Copy sample syllabus to test PDF upload
cp sample_syllabus.txt test_syllabus.txt
```
- Upload from browser file input (Note: currently accepts text/pasted content)

### Test Google Calendar (if credentials set)
- [ ] Create `.env` file in root with Google OAuth credentials:
  ```
  GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your-secret
  ```
- [ ] Restart backend
- [ ] Should see "Connect to Google Calendar" button in UI

### Test OCR (Optional)
- [ ] Install Tesseract (see `TROUBLESHOOTING.md`)
- [ ] Upload image with text
- [ ] Should extract text automatically

---

## ✅ Common Issues During Setup

### "npm: command not found"
- Install Node.js from https://nodejs.org
- Restart terminal
- Test: `npm --version`

### "ModuleNotFoundError: No module named 'fastapi'"
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### "Port 8000 already in use"
- Kill existing process: `lsof -i :8000 | grep python | awk '{print $2}' | xargs kill`
- Or use different port: `uvicorn backend.main:app --port 8001`

### "npm install hangs"
- Clear npm cache: `npm cache clean --force`
- Try again: `npm install`

### Browser shows blank page at http://localhost:5173
- Check Terminal 2 for errors
- Restart dev server: `npm run dev`
- Clear browser cache: Ctrl+Shift+Del

---

## ✅ Development Tools

### Browser DevTools (F12)
- [ ] Check Console tab for errors
- [ ] Check Network tab to see API calls
- [ ] Check Application tab to see local storage

### Backend API Docs
- [ ] Visit http://localhost:8000/docs
- [ ] See all available endpoints
- [ ] Test endpoints directly from Swagger UI

### VS Code Extensions (Recommended)
- [ ] **ES7+ React/Redux/React-Native snippets** (dsznajder.es7-react-js-snippets)
- [ ] **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
- [ ] **Python** (ms-python.python)
- [ ] **FastAPI** (MariusAlchimavicius.fastapi)

---

## ✅ Next Steps After Setup

1. ✅ **Master Local Development**
   - Make small changes to components
   - Watch hot reload in action
   - Get comfortable with workflow

2. ✅ **Explore the Code**
   - Read `frontend/src/lib/api.ts` - understand API calls
   - Read `frontend/src/components/PlanForm.tsx` - form logic
   - Read `backend/main.py` - endpoint implementations

3. ✅ **Deploy to Vercel** (When ready)
   - Follow [`QUICKSTART.md`](./QUICKSTART.md) Phase 2
   - Push to GitHub
   - Connect to Vercel
   - Deploy with one click

4. ✅ **Enhance UI with v0.dev** (Optional)
   - Follow [`FRONTEND_SETUP.md`](./FRONTEND_SETUP.md) Part 2
   - Upload components to v0.dev
   - Get AI-generated UI improvements

---

## ✅ Troubleshooting

For detailed troubleshooting, see [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md)

Quick links:
- Backend crashes: https://github.com/Planora/issues (check existing issues)
- Frontend not loading: Clear cache, restart `npm run dev`
- API errors: Check http://localhost:8000/docs for endpoint info
- Database errors: Delete `backend/plans.db` to reset

---

## ✅ You're Ready!

Once all checkboxes above are complete, you're ready to:
- Develop new features
- Deploy to production
- Use v0.dev for AI design
- Share with friends/classmates

---

**Time to Completion:** ~20–30 minutes (first time)

**Questions?** See:
- [`README.md`](./README.md) - Project overview
- [`FRONTEND_SETUP.md`](./FRONTEND_SETUP.md) - Detailed setup
- [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) - Common issues
- http://localhost:8000/docs - API documentation

---

**Happy Coding! 🚀**
