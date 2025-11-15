# Quick Start Checklist: Planora Frontend

Use this checklist to get Planora running and deployed.

## ✅ Phase 1: Local Development (5 minutes)

- [ ] Install Node.js v18+ from https://nodejs.org
- [ ] Verify Node: `node --version && npm --version`
- [ ] Navigate to frontend: `cd /workspaces/Planora/frontend`
- [ ] Install dependencies: `npm install`
- [ ] Start dev server: `npm run dev`
- [ ] Open browser: http://localhost:5173
- [ ] Ensure backend is running: `uvicorn backend.main:app --reload` (in another terminal)
- [ ] Create account / log in at frontend
- [ ] Test plan generation (upload syllabus or manual topics)
- [ ] ✅ Everything works locally!

---

## ✅ Phase 2: Push to GitHub (5 minutes)

- [ ] Initialize git (if not already): `cd /workspaces/Planora && git init`
- [ ] Add remote: `git remote add origin <YOUR-REPO-URL>`
- [ ] Stage changes: `git add .`
- [ ] Commit: `git commit -m "Add Planora AI study planner"`
- [ ] Push: `git push -u origin main`
- [ ] ✅ Code is on GitHub!

---

## ✅ Phase 3: Deploy to Vercel (10 minutes)

### Frontend Deployment:
- [ ] Go to https://vercel.com and sign in
- [ ] Click **Add New Project** → **Import Git Repository**
- [ ] Select your Planora repository
- [ ] Framework: **Vite**
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Click **Deploy**
- [ ] Wait for deployment (2–5 minutes)
- [ ] ✅ Frontend is live at vercel URL!

### Set Backend URL:
- [ ] In Vercel dashboard: **Settings** → **Environment Variables**
- [ ] Add `VITE_API_URL` = `http://localhost:8000` (for now)
- [ ] Later, update to deployed backend URL
- [ ] **Redeploy** to apply changes
- [ ] ✅ Frontend connects to backend!

---

## ✅ Phase 4: Enhance UI with v0.dev (Optional, 10–30 minutes)

- [ ] Go to https://v0.dev and sign in with Vercel
- [ ] Create new project
- [ ] Copy component code from `frontend/src/components/` to v0
- [ ] Example prompts:
  - "Add dark mode to this component"
  - "Make it more modern with glassmorphism and animations"
  - "Improve mobile responsiveness"
- [ ] Export improved code from v0
- [ ] Replace local component files
- [ ] Test locally: `npm run dev`
- [ ] Commit & push: `git add . && git commit -m "UI enhancements from v0" && git push`
- [ ] ✅ Vercel auto-deploys!

---

## ✅ Phase 5: Deploy Backend (Optional, 15–30 minutes)

### Option A: Railway (Recommended)
- [ ] Go to https://railway.app
- [ ] Sign in with GitHub
- [ ] Create new project from GitHub repo
- [ ] Select `main` branch
- [ ] Set environment variables:
  - `GOOGLE_CLIENT_ID` (if using Google Calendar)
  - `GOOGLE_CLIENT_SECRET`
  - `ENCRYPTION_KEYS` (comma-separated old keys, or use admin rotate_keys)
  - `DB_PATH` (can be `backend/plans.db` for SQLite on Railway)
- [ ] Deploy
- [ ] Copy backend URL (e.g., https://planora-api.railway.app)

### Option B: Render
- [ ] Similar to Railway; connect GitHub repo
- [ ] Use Python 3.11 environment
- [ ] Run command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- [ ] Set env vars (same as Railway)

### Option C: VPS (Digital Ocean, AWS, etc.)
- [ ] SSH into server
- [ ] Clone repo: `git clone <YOUR-REPO-URL>`
- [ ] Set up systemd service (see `deploy/planora-backend.service`)
- [ ] Use Nginx as reverse proxy
- [ ] Enable HTTPS with Let's Encrypt

### Update Frontend with Backend URL:
- [ ] In Vercel: **Settings** → **Environment Variables**
- [ ] Update `VITE_API_URL` = `https://your-backend-domain.com`
- [ ] Redeploy
- [ ] ✅ Production app is fully live!

---

## ✅ Final Verification

- [ ] Frontend loads at Vercel URL
- [ ] Backend is accessible from frontend
- [ ] Can register/login
- [ ] Can generate a plan
- [ ] Can save/load plans
- [ ] Can export PDF
- [ ] (Optional) Google Calendar integration works

---

## 📚 Additional Resources

- **Full Setup Guide**: `/workspaces/Planora/FRONTEND_SETUP.md`
- **Frontend README**: `/workspaces/Planora/frontend/README.md`
- **Vite Docs**: https://vitejs.dev
- **Vercel Docs**: https://vercel.com/docs
- **v0.dev**: https://v0.dev
- **Railway**: https://railway.app

---

## 🚀 You're Done!

Your Planora study planner is now live and ready for users. 

**Next Steps:**
1. Share the Vercel URL with friends/classmates
2. Collect feedback and iterate on v0.dev
3. Monitor backend logs for errors
4. Update backend URL in Vercel as needed

Happy planning! 📚
