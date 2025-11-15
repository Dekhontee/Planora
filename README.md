# 📚 Planora — AI Study Plan Generator

An AI-powered tool that creates personalized, day-by-day study plans for students. Upload a syllabus, set your exam date and available study hours, and Planora generates an optimized plan with daily goals, time blocks, and practice problem suggestions.

## ⭐ Features (MVP)

- **✅ Syllabus Upload**: Upload PDF or paste syllabus text
- **✅ Personalized Plans**: 7-, 14-, or 30-day study plans
- **✅ Time-Blocking**: Allocates study time proportionally to topic difficulty
- **✅ Daily Summaries**: Clear "Today's goal" for each day
- **✅ Review Days**: Built-in review days (every 7 days) for reinforcement
- **✅ Course Types**: Supports Chemistry, Calculus, Engineering, and more
- **✅ Practice Suggestions**: AI-recommended problem counts per topic
- **✅ Export Options**: Download plan as JSON or text file

## 🛠 Tech Stack

### Backend
- **FastAPI** + Python 3.11
- **SQLite** for persistence (users, plans, OAuth tokens)
- **pdfplumber + pytesseract** for PDF parsing and OCR
- **Fernet encryption** for secure token storage with key rotation
- **OAuth 2.0** for Google Calendar integration

### Frontend Options

**Legacy (Streamlit)** - Simple, all-in-one Python UI
- Single-file deployment
- Real-time features (sliders, checkboxes)
- No build step required

**Modern (React + Vite)** - Recommended, production-ready
- React 18 + TypeScript
- Vite for fast dev experience and builds
- Tailwind CSS for styling
- Axios for API client
- Radix UI components
- **Deployment Ready**: Vercel, v0.dev compatible
- Dark mode support
- Responsive design

### Infrastructure & Deployment
- **Vercel** for frontend hosting (React only)
- **Railway/Render/VPS** for backend deployment
- **v0.dev** for AI-assisted UI enhancement

## 📋 Setup & Installation

### Prerequisites
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend - React only)
- **npm or yarn** (frontend - React only)

### Quick Start

**For Streamlit (Legacy) Frontend:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Terminal 1: Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (Streamlit)
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

---

**For React (Recommended) Frontend:**

See **[QUICKSTART.md](./QUICKSTART.md)** for detailed setup instructions including Vercel deployment and v0.dev integration.

```bash
# Install dependencies
pip install -r requirements.txt  # Backend
cd frontend && npm install       # Frontend

# Terminal 1: Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (React + Vite)
cd frontend && npm run dev
```

Open http://localhost:5173 in your browser.

---

### Full Documentation

- **React Frontend Setup**: [`frontend/README.md`](./frontend/README.md)
- **Full Setup & Deployment Guide**: [`FRONTEND_SETUP.md`](./FRONTEND_SETUP.md)
- **Quick Start Checklist**: [`QUICKSTART.md`](./QUICKSTART.md)

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/Dekhontee/Planora.git
cd Planora
pip install -r requirements.txt
```

### 2. Start the FastAPI Backend

**Option A: Direct Python**
```bash
python3 backend/main.py
```

**Option B: Using run script**
```bash
bash run_backend.sh
```

The backend will start at `http://localhost:8000`. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. (In a new terminal) Start the Frontend

**Streamlit (Legacy):**
```bash
streamlit run streamlit_app.py
```
Runs on http://localhost:8501

**React (Recommended):**
```bash
cd frontend
npm install
npm run dev
```
Runs on http://localhost:5173

## 🚀 Quick Start

### For Streamlit (Legacy)
1. Run `bash run_backend.sh` (Terminal 1)
2. Run `bash run_frontend.sh` (Terminal 2)
3. Open http://localhost:8501

### For React (Recommended)
See [**QUICKSTART.md**](./QUICKSTART.md) for full setup.

Quick version:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend && npm install && npm run dev
```
Open http://localhost:5173

### Deploy to Vercel (React Only)
```bash
git push origin main
# → Vercel auto-deploys on GitHub push
# Frontend: https://planora-xxxx.vercel.app
```

See [**FRONTEND_SETUP.md**](./FRONTEND_SETUP.md) for complete deployment instructions including v0.dev integration.

---

## 🎨 Using v0.dev for AI UI Design

Planora's React frontend is fully compatible with **v0.dev** (Vercel's AI code generator). Enhance the UI with AI:

1. Visit https://v0.dev and sign in with Vercel
2. Import React components from `frontend/src/`
3. Prompt v0 to enhance design:
   - "Add dark mode and animations"
   - "Make it look modern with glassmorphism"
   - "Improve mobile responsiveness"
4. Export improved code back to your frontend
5. Deploy to Vercel with `git push`

See [**FRONTEND_SETUP.md**](./FRONTEND_SETUP.md) (Part 2) for detailed v0.dev instructions.

## 📄 Project Structure

```
Planora/
├── backend/
│   ├── main.py                 # FastAPI app + all endpoints
│   ├── parser.py               # Syllabus parsing & plan generation
│   ├── ml_models.py            # Optional ML models
│   ├── plans.db                # SQLite database (users, plans, tokens)
│   └── __init__.py
├── frontend/                    # React + Vite frontend (NEW!)
│   ├── src/
│   │   ├── components/
│   │   │   ├── PlanForm.tsx
│   │   │   ├── PlanDisplay.tsx
│   │   │   └── ui/             # Button, Card, Input, etc.
│   │   ├── lib/
│   │   │   ├── api.ts          # Axios API client
│   │   │   └── utils.ts
│   │   ├── App.tsx             # Main app
│   │   ├── main.tsx            # Entry point
│   │   └── index.css           # Tailwind styles
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── README.md
├── streamlit_app.py            # Legacy Streamlit frontend
├── requirements.txt            # Python dependencies
├── sample_syllabus.txt         # Example syllabus
├── run_backend.sh
├── run_frontend.sh
├── FRONTEND_SETUP.md           # Detailed setup & deployment guide
├── QUICKSTART.md               # Quick reference checklist
├── deploy/                     # Deployment configs
│   ├── planora-backend.service
│   ├── planora-frontend.service
│   └── supervisor.conf
├── scripts/
│   └── admin_rotate_keys.py    # Admin key rotation utility
├── tests/
│   └── test_api.py             # API tests (pytest)
└── README.md                   # This file
```

## 🔍 How It Works

### 1. Syllabus Parsing (`backend/parser.py`)
- Extracts chapters/sections from PDF or text
- Identifies topic structure and content length
- Groups chapters into study topics
- Works with both structured and semi-structured syllabi

### 2. Plan Generation
- Calculates total available study time: `days × hours_per_day × 60 minutes`
- Allocates time per topic proportionally to content length
- Distributes topics across days, respecting daily hour limits
- Inserts review days every 7 days
- Generates daily summaries and practice problem suggestions (estimated as `time / 10`)

### 3. Frontend Display (Streamlit)
- Modern card-based layout showing each day's goals
- Topic breakdown with time estimates
- Special highlighting for review days
- Real-time form submission and plan generation
- Export to JSON or text format

## 🧪 Testing the Backend Directly

### Quick Test
```bash
bash demo_backend.sh
```

### Manual cURL Test with Text
```bash
curl -X POST http://localhost:8000/plan \
  -F "syllabus_text=Chapter 1: Basics. Chapter 2: Advanced Topics. Chapter 3: Applications." \
  -F "exam_date=2025-12-15" \
  -F "hours_per_day=2.0" \
  -F "plan_length=14" \
  -F "course_type=Chemistry"
```

### Test with PDF File
```bash
curl -X POST http://localhost:8000/plan \
  -F "file=@path/to/syllabus.pdf" \
  -F "exam_date=2025-12-15" \
  -F "hours_per_day=2.0" \
  -F "plan_length=14"
```

## 🎓 Example Usage

### Sample Syllabus Format

Your syllabus should include chapters or topics. The parser extracts them automatically:

```
Chapter 1: Introduction
This covers the basics...

Chapter 2: Core Concepts
More advanced material...

Chapter 3: Applications
Practical examples...
```

See `sample_syllabus.txt` for a complete example.

## 🤖 Optional: TensorFlow Difficulty Predictor

To enable AI-powered difficulty prediction:

```bash
# Install TensorFlow
pip install tensorflow

# Train the model on sample data
python3 backend/ml_models.py
```

## 🖨️ OCR / EasyOCR / Tesseract

This project supports OCR for images containing topic lists. There are two options:

- Tesseract (recommended for printed text): install the system binary and Python wrapper:

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y tesseract-ocr
pip install pytesseract Pillow
```

- EasyOCR (can be better for handwriting, but requires PyTorch):

```bash
pip install easyocr
# This may pull in a torch build. If you have a GPU and want to use it, you can enable the "Use OCR GPU" checkbox in the UI. EasyOCR will use GPU if available and supported.
```

If neither is available, the UI will warn that OCR isn't available and ask you to paste topics or upload a PDF/text syllabus instead.

This creates a `backend/difficulty_model.h5` file that can be used to predict topic difficulty and adjust study time estimates accordingly.

**Note**: The heuristic version works without TensorFlow and is suitable for the MVP. TensorFlow is optional for enhanced predictions.

## 🎯 Next Steps / Future Features

### Coming Soon (Post-Hackathon)
1. **Enhanced TensorFlow Model**
   - Classify topics by difficulty (1–5 scale)
   - Adjust time allocation based on predicted complexity
   - Train on larger student datasets

2. **LLM Integration**
   - Use OpenAI/Gemini APIs for smarter plan generation
   - Generate context-aware study tips
   - Personalized practice problem recommendations

3. **Smart Scheduling**
   - Prioritize harder topics earlier
   - Detect topic prerequisites and reorder accordingly
   - Adaptive rescheduling based on progress

4. **Persistence & Export**
   - Save plans to database (SQLite/PostgreSQL)
   - Email daily reminders
   - Google Calendar integration
   - PDF export with formatting

5. **User Accounts** (Optional)
   - Track progress through the plan
   - Historical plan data and analytics
   - Collaborative planning for study groups

## 🏗 Architecture Diagram

```
                          ┌─────────────────────────────┐
                          │  v0.dev (Optional)          │
                          │  AI UI Enhancement          │
                          └──────────────┬──────────────┘
                                         │
              ┌──────────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │  Frontend Options:           │
    │  • React + Vite (Vercel)     │ ◄──────── (RECOMMENDED)
    │  • Streamlit (Local)         │
    └──────────┬───────────────────┘
               │
        (HTTP API via /api/*)
               │
               ▼
    ┌──────────────────────────────┐
    │  FastAPI Backend             │
    │  localhost:8000              │
    └──────────┬───────────────────┘
               │
    ┌──────────┼──────────┬─────────────┐
    │          │          │             │
    ▼          ▼          ▼             ▼
  Parser   SQLite DB  Google OAuth  Key Rotation
 (PDF/OCR)  (Plans)   (Calendar)     (Admin)
```

## 💡 Hackathon Tips

- **MVP Focus**: Core parsing + simple plan generation (✅ Done)
- **Quick Wins**: Add color-coded difficulty, practice problem counts (✅ Done)
- **Demo Script**:
  1. Run `bash demo_backend.sh` to show API
  2. Open Streamlit UI at `http://localhost:8501`
  3. Upload `sample_syllabus.txt` or paste text
  4. Set exam date to 30 days away
  5. Show generated 14-day plan
  6. Highlight review days and daily summaries
  7. Download plan as JSON
  8. Discuss TensorFlow + LLM roadmap

- **Pitch**: "Students waste time planning. Planora removes guesswork—upload syllabus, get instant personalized schedule. Ready to study smarter? 📚"

## 🧪 Running the Full Stack

### Option 1: Streamlit Frontend (Legacy)

**Terminal 1 - Backend:**
```bash
python3 backend/main.py
# or: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py
```

Browser: http://localhost:8501

---

### Option 2: React Frontend (Recommended)

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Browser: http://localhost:5173

---

### Option 3: Full Production Setup

See [**FRONTEND_SETUP.md**](./FRONTEND_SETUP.md) (Parts 1–5) for:
- Local development setup
- v0.dev integration (AI UI enhancement)
- Vercel deployment (frontend)
- Railway/Render deployment (backend)
- Environment variable configuration

## 📝 License

MIT License — see LICENSE file.

## 👨‍💻 Contributors

Built during a hackathon by @Dekhontee

---

**Questions or issues?** 
- Check the [FastAPI docs](https://fastapi.tiangolo.com/)
- Check the [Streamlit docs](https://docs.streamlit.io/)
- Review `sample_syllabus.txt` for input format examples


