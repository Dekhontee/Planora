# Planora Frontend Setup & Deployment Guide

This guide walks you through setting up the Planora React frontend locally, integrating with v0.dev for AI-assisted UI enhancement, and deploying to Vercel.

---

## Part 1: Local Development Setup

### Step 1: Prerequisites

Ensure you have:
- **Node.js** v18+ ([download](https://nodejs.org))
- **npm** (comes with Node.js)
- **Backend running** on `http://localhost:8000`

### Step 2: Install Frontend Dependencies

```bash
cd /workspaces/Planora/frontend
npm install
```

This will install all dependencies listed in `package.json`:
- React, React DOM, Vite, TypeScript
- Tailwind CSS, PostCSS, Autoprefixer
- Axios (HTTP client)
- Lucide React (icons)
- Radix UI primitives

### Step 3: Start Development Server

```bash
npm run dev
```

You'll see output like:
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

Open http://localhost:5173 in your browser. The Vite dev server will automatically proxy API requests to `http://localhost:8000` (configured in `vite.config.ts`).

### Step 4: Verify Backend is Running

In another terminal:
```bash
cd /workspaces/Planora
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Test the App

1. Navigate to http://localhost:5173
2. Register a new account or log in
3. Try uploading a syllabus or entering manual topics
4. Set exam date, hours per day, plan length
5. Click "Generate Plan" to create a study plan
6. Check/uncheck study days, save the plan
7. Try exporting as PDF or JSON

---

## Part 2: Integration with v0.dev (AI Code Generation)

v0.dev is Vercel's AI-powered code generation platform. Use it to enhance the Planora UI with modern designs, dark mode, animations, and more.

### Step 1: Sign Up for v0.dev

1. Visit https://v0.dev
2. Click **Sign In** → **Sign in with Vercel**
3. Authorize with your Vercel account (create one if needed at https://vercel.com)

### Step 2: Create a v0 Project

**Option A: Start from Scratch**
1. Click **New Project** → **Create New**
2. Give it a name: `planora-frontend`
3. v0 will open a blank canvas

**Option B: Import from Code**
1. Go to https://v0.dev → **New Project** → **Import Code**
2. Paste the contents of any React component from `frontend/src/components/` (e.g., `PlanForm.tsx`, `PlanDisplay.tsx`)
3. v0 will parse and display the component

### Step 3: Prompt v0 to Enhance the UI

Here are example prompts you can use:

#### Prompt 1: Add Dark Mode
```
Add dark mode support to this React component. 
Include a toggle button in the header to switch between light and dark themes.
Use Tailwind dark: prefix for styling.
```

#### Prompt 2: Improve Plan Display
```
Enhance the study plan display with:
- Animated progress bars for completion %
- Smooth fade-in animations when cards load
- Color-coded difficulty levels for topics
- Better visual hierarchy with improved spacing
```

#### Prompt 3: Modernize Form Design
```
Redesign this study plan form with:
- Glassmorphism effect on form cards
- Smooth transitions and hover effects
- Better input field styling with icons
- Cleaner typography and spacing
- Responsive design for mobile and tablet
```

#### Prompt 4: Add Navigation & Layout
```
Create a modern dashboard layout with:
- A left sidebar navigation menu
- Breadcrumb navigation
- Better spacing and grid layout
- Dark mode support
- Mobile hamburger menu
```

### Step 4: Export and Integrate

1. Once v0 generates an improved component, click **Copy Code** or **Export**
2. Paste the code into your local `frontend/src/components/` file (backup the original first)
3. Test locally: `npm run dev`
4. Commit changes to git
5. Push to GitHub → Vercel auto-deploys

---

## Part 3: Deployment to Vercel

### Step 1: Push Code to GitHub

```bash
cd /workspaces/Planora
git add .
git commit -m "Add React frontend with Vite and Tailwind CSS"
git push origin main
```

(If not yet a git repo: `git init && git remote add origin <your-repo-url>`)

### Step 2: Connect to Vercel

1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. Select **Import Git Repository** → authorize GitHub
4. Select the `Planora` repository
5. Under **Project Settings**:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
6. Click **Deploy**

Vercel will build and deploy the frontend to a URL like `https://planora-xxxx.vercel.app`.

### Step 3: Set Environment Variables

1. In Vercel dashboard, go to your project → **Settings** → **Environment Variables**
2. Add a new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-domain.com` (replace with actual backend URL)
   - **Environments**: `Production`
3. Click **Save**
4. Redeploy: **Deployments** → **Redeploy** (select latest commit)

### Step 4: Deploy Backend (Optional)

The backend can be deployed to:
- **Railway.app**: Free tier available, simple Git integration
- **Render.com**: Similar to Railway, good free tier
- **AWS/GCP/Azure**: More complex, but scalable

For this guide, we'll assume backend stays on your local machine or a VPS.

---

## Part 4: Full Deployment Workflow

Here's a complete workflow for iterating on the UI and deploying:

1. **Local Development** (on your machine):
   ```bash
   # Terminal 1: Backend
   cd /workspaces/Planora
   uvicorn backend.main:app --reload
   
   # Terminal 2: Frontend
   cd /workspaces/Planora/frontend
   npm run dev
   ```

2. **Visit http://localhost:5173**, test features

3. **Use v0.dev to enhance UI**:
   - Copy component code to v0.dev
   - Prompt v0 to improve design
   - Export improved code

4. **Integrate Improvements**:
   - Replace old component files with v0 exports
   - Test locally
   - Commit changes

5. **Deploy to Vercel**:
   ```bash
   git add .
   git commit -m "Improve UI with v0 AI design"
   git push origin main
   ```
   Vercel auto-deploys on push.

---

## Part 5: Environment Configuration

### Development (.env)

Create `.env` in `frontend/`:
```
VITE_API_URL=http://localhost:8000
```

### Production (Vercel)

Set in Vercel project settings:
- `VITE_API_URL`: Your deployed backend URL (e.g., `https://planora-api.example.com`)

---

## Part 6: Troubleshooting

### "npm: command not found"
- Install Node.js from https://nodejs.org
- Verify: `node --version && npm --version`

### "Cannot GET http://localhost:5173"
- Ensure `npm run dev` is running
- Check terminal for errors
- Try clearing cache: `rm -rf node_modules package-lock.json && npm install`

### "API calls returning 404"
- Verify backend is running on `http://localhost:8000`
- Check `vite.config.ts` proxy config
- Inspect browser console (F12 → Network tab) to see actual request URLs

### "Tailwind styles not applying"
- Ensure all CSS classes are in `src/` files (not ignored by config)
- Run `npm run build` to test production build
- Check `tailwind.config.js` for correct `content` paths

### v0.dev Component Not Working Locally
- Make sure v0-generated code is React compatible
- Check for missing imports (add `import React from 'react'` if needed)
- Verify component receives correct props
- Check browser console for errors

---

## Part 7: Next Steps

1. ✅ Set up local dev environment (npm install, npm run dev)
2. ✅ Ensure backend is running (uvicorn backend.main:app)
3. ✅ Use v0.dev to design UI improvements
4. ✅ Deploy frontend to Vercel
5. ✅ Deploy backend to Railway/Render (or keep on VPS)
6. ✅ Configure VITE_API_URL in Vercel for production backend URL
7. ✅ Monitor and iterate

---

## Quick Reference

| Task | Command |
|------|---------|
| Install deps | `npm install` |
| Dev server | `npm run dev` |
| Build for prod | `npm run build` |
| Preview build | `npm run preview` |
| Backend | `uvicorn backend.main:app --reload` |

---

## Resources

- **Vite Docs**: https://vitejs.dev
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **v0.dev**: https://v0.dev
- **Vercel Docs**: https://vercel.com/docs
- **Shadcn/ui**: https://ui.shadcn.com

---

Happy coding! 🚀
