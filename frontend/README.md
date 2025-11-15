# Planora Frontend

A modern React + TypeScript + Vite frontend for Planora, an AI-powered study plan generator.

## Local Development Setup

### Prerequisites
- Node.js (v18+)
- npm or yarn
- Backend running on `http://localhost:8000` (see root `/workspaces/Planora/README.md`)

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173` and will proxy API calls to `http://localhost:8000`.

### Environment Variables

Create a `.env` file in the `frontend/` directory (optional):
```
VITE_API_URL=http://localhost:8000
```

If not set, the default is `http://localhost:8000` via the Vite proxy config in `vite.config.ts`.

## Building for Production

```bash
npm run build
```

The optimized build will be generated in the `dist/` directory, ready for deployment to Vercel, Netlify, or any static hosting.

## Deployment to Vercel

1. Push the repository to GitHub.
2. Connect the repo to Vercel:
   - Visit https://vercel.com and sign in.
   - Import the repository.
   - Set project root to `frontend/`.
3. In Vercel project settings, add environment variable:
   - `VITE_API_URL` = `https://your-backend-domain.com` (update with actual backend URL)
4. Deploy—Vercel will automatically run `npm install && npm run build`.

## Integration with v0.dev

v0.dev is Vercel's AI code generation platform. To enhance the UI with AI:

1. Visit https://v0.dev and sign in with your Vercel account.
2. Create a new project or import code from `frontend/src/`.
3. Provide a prompt to enhance the UI. Example prompts:
   - "Add dark mode support to the Planora study planner UI"
   - "Improve the plan display with animated progress bars and smooth transitions"
   - "Add a sidebar navigation and make the layout responsive"
   - "Create a glassmorphism design for cards and buttons"
4. v0 will generate improved components; export and integrate them back.

## Tech Stack

- **React 18** – UI framework
- **TypeScript** – Type-safe development
- **Vite** – Fast build tool and dev server
- **Tailwind CSS** – Utility-first styling
- **shadcn/ui** – Radix UI component library (styled with Tailwind)
- **Axios** – HTTP client for API calls
- **Lucide React** – Icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── PlanForm.tsx       # Study plan form input
│   │   ├── PlanDisplay.tsx    # Plan display with checkboxes
│   │   └── ui/                # Reusable UI components (button, card, input, etc.)
│   ├── lib/
│   │   ├── api.ts             # Axios API client
│   │   └── utils.ts           # Utility functions (cn, etc.)
│   ├── App.tsx                # Main app layout
│   ├── main.tsx               # React root entry
│   └── index.css              # Global styles (Tailwind)
├── package.json               # Dependencies
├── vite.config.ts             # Vite config (React plugin, proxy)
├── tailwind.config.js         # Tailwind theme
├── postcss.config.js          # PostCSS with Tailwind
└── tsconfig.json              # TypeScript config
```

## Available Scripts

- `npm run dev` – Start dev server
- `npm run build` – Build for production
- `npm run preview` – Preview production build locally
- `npm run lint` – Run ESLint (if configured)

## Notes

- The API client in `src/lib/api.ts` handles all communication with the backend.
- State management uses React hooks (useState, useEffect).
- Styling is entirely Tailwind CSS; no external CSS files needed after build.
- Dark mode ready via CSS variables in `index.css`.
