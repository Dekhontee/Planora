# Planora Troubleshooting Guide

This guide helps resolve common issues when setting up and running Planora.

---

## Backend Issues

### "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Python dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

Verify: `pip list | grep fastapi`

---

### "Address already in use" on port 8000

**Cause:** Another process is using port 8000

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
uvicorn backend.main:app --port 8001
```

---

### "SQLite database locked"

**Cause:** Multiple processes accessing database simultaneously

**Solution:**
```bash
# Close all Planora processes
# Delete corrupted database
rm backend/plans.db

# Restart backend (will recreate database)
uvicorn backend.main:app --reload
```

---

### OCR Not Working / "Tesseract not found"

**Cause:** pytesseract installed but system tesseract binary missing

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

**Solution (Mac):**
```bash
brew install tesseract
```

**Alternative:** Use EasyOCR instead
```bash
pip install easyocr
# Check "Use OCR GPU" in UI if you have a GPU
```

---

### "No module named 'pdfplumber'"

**Cause:** PDF parsing library not installed

**Solution:**
```bash
pip install pdfplumber
```

---

### Backend crashes when uploading PDF

**Cause:** PDF parsing error or memory issue

**Solution:**
```bash
# Check Python logs for detailed error
# Try smaller PDF first
# Increase memory: python -u backend/main.py
# Or use text input instead of PDF
```

---

## Frontend Issues (Streamlit)

### "Module not found: streamlit"

**Cause:** Streamlit not installed

**Solution:**
```bash
pip install streamlit
```

---

### "ConnectionRefusedError: [Errno 111] Connection refused" at 127.0.0.1:8000

**Cause:** Backend not running

**Solution:**
```bash
# Terminal 1: Start backend
uvicorn backend.main:app --reload

# Terminal 2: Start Streamlit
streamlit run streamlit_app.py
```

---

### Streamlit app shows "register" but register button doesn't work

**Cause:** API endpoint returning 404

**Solution:**
- Check backend logs for errors
- Verify backend is running on port 8000
- Try Streamlit app's retry mechanism (auto-retries with trailing slash)

---

### File uploader not working

**Cause:** Temporary file permissions issue

**Solution:**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/

# Restart Streamlit
streamlit run streamlit_app.py
```

---

## Frontend Issues (React)

### "npm: command not found"

**Cause:** Node.js not installed

**Solution:**
- Download and install Node.js v18+ from https://nodejs.org
- Verify: `node --version && npm --version`

---

### "Cannot find module" when running `npm run dev`

**Cause:** Dependencies not installed

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

### "EADDRINUSE: address already in use :::5173"

**Cause:** Another process using Vite port 5173

**Solution:**
```bash
# Kill process
lsof -i :5173 | grep node | awk '{print $2}' | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

---

### Vite dev server running but http://localhost:5173 shows blank page

**Cause:** Frontend didn't compile or build error

**Solution:**
1. Check terminal for TypeScript/build errors
2. Clear browser cache: Ctrl+Shift+Del (Chrome)
3. Restart dev server: `npm run dev`
4. Check browser console (F12) for errors

---

### "Cannot reach backend at http://localhost:8000"

**Cause:** Backend not running or port mismatch

**Solution:**
```bash
# Verify backend is running
ps aux | grep uvicorn

# Check port
curl http://localhost:8000/docs

# If not running, start it
uvicorn backend.main:app --reload
```

---

### API calls returning 404 or 500

**Cause:** Backend not running or endpoint missing

**Solution:**
1. Check backend logs: Look for error messages
2. Test endpoint directly:
   ```bash
   curl -X GET http://localhost:8000/docs
   ```
3. Verify Vite proxy config in `frontend/vite.config.ts`:
   ```typescript
   proxy: {
     '/api': {
       target: 'http://localhost:8000',
       rewrite: (path) => path.replace(/^\/api/, '')
     }
   }
   ```

---

## Deployment Issues

### Vercel Build Fails

**Common Causes:**
- Node version mismatch
- Missing environment variables
- Build script error

**Solution:**
```bash
# Test build locally
cd frontend
npm run build

# Check for errors in output
# Verify .env variables are set in Vercel project settings
```

---

### "VITE_API_URL not defined" on Vercel

**Cause:** Environment variable not set in Vercel

**Solution:**
1. Go to Vercel project → Settings → Environment Variables
2. Add `VITE_API_URL` = `https://your-backend-url.com`
3. Redeploy: Deployments → Redeploy (latest commit)

---

### v0.dev Import Fails

**Cause:** Component code has syntax errors or missing imports

**Solution:**
- Ensure React imports are present: `import React from 'react'`
- Check for TypeScript syntax errors
- Paste one component at a time, not entire files

---

## Performance Issues

### App is Slow / Generating Plan Takes >10 Seconds

**Cause:** Large syllabus or parsing inefficiency

**Solution:**
```bash
# Try with smaller syllabus first
# Or use text instead of PDF
# Check backend logs for slow operations
```

---

### Frontend takes long time to load

**Cause:** Large bundle size

**Solution:**
```bash
# Check bundle size
npm run build
ls -lh frontend/dist/

# Consider code splitting or lazy loading
```

---

## Getting Help

1. **Check logs:**
   - Backend: Look at uvicorn terminal output
   - Frontend: Open browser DevTools (F12) → Console tab
   - Streamlit: Check terminal for error messages

2. **Enable verbose logging (Python):**
   ```bash
   # Set log level
   LOGLEVEL=DEBUG uvicorn backend.main:app --reload
   ```

3. **Test backend directly:**
   ```bash
   # Open Swagger UI
   curl http://localhost:8000/docs
   ```

4. **Clear cache and reinstall:**
   ```bash
   # Frontend
   cd frontend && rm -rf node_modules package-lock.json && npm install
   
   # Backend
   rm -rf backend/__pycache__ && pip install --upgrade -r requirements.txt
   ```

5. **Check firewall:**
   ```bash
   # Ensure ports are open
   sudo ufw allow 8000
   sudo ufw allow 8501
   sudo ufw allow 5173
   ```

---

## Still Having Issues?

1. Check the main README: [README.md](./README.md)
2. Review API docs at http://localhost:8000/docs (when backend running)
3. Check error stack traces carefully
4. Try the minimal example: Upload `sample_syllabus.txt`, generate plan, check output

---
