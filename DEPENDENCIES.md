# Atlas — Dependencies & what you need to run this

Small inventory of libraries, tools, and external services used by this repo
(as of the Course Directory, auth/email, Google Sign-In, recommendations, and
challenge-image work).

Canonical install lists:
- Backend: `smarttrack-backend/requirements.txt`
- Frontend: `smarttrack-frontend/package.json`
- Env template: `smarttrack-backend/.env.example`

---

## 1. System (install on the machine)

| Tool | Used for |
|------|----------|
| **Python 3.11+** (3.12–3.14 ok) | FastAPI backend |
| **Node.js 20+** + npm | Next.js frontend |
| **PostgreSQL 14+** | App database (local or Neon) |
| **Git** | Version control |

Optional: `openssl` (generate `SECRET_KEY`).

---

## 2. Backend Python packages

Install:

```bash
cd smarttrack-backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

| Package | Role |
|---------|------|
| `fastapi` | HTTP API |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy` + `psycopg[binary]` | Async Postgres ORM / driver |
| `alembic` | DB migrations |
| `passlib[bcrypt]` | Password hashing |
| `python-jose[cryptography]` | JWT (login + password-reset tokens) |
| `python-multipart` | Form / file uploads (e.g. WASSCE) |
| `authlib` + `httpx` | Google OAuth + Resend HTTP + LLMs |
| `pydantic` + `pydantic-settings` + `python-dotenv` | Settings / `.env` |
| `email-validator` | Email field validation |
| `pypdf` | Academic PDF grade extraction |
| `scikit-learn` + `joblib` + `pandas` + `numpy` | KNUST ML alternate recommendations |

**No separate Resend SDK** — email uses `httpx` → Resend REST API (`app/mailer.py`).

---

## 3. Frontend npm packages

Install:

```bash
cd smarttrack-frontend
npm install
```

### Runtime

| Package | Role |
|---------|------|
| `next` | App framework (App Router) |
| `react` / `react-dom` | UI |
| `framer-motion` | Motion (dashboard, pages) |
| `lucide-react` | Icons |
| `clsx` + `tailwind-merge` | ClassName helpers |
| `react-markdown` + `remark-gfm` | Lesson / markdown rendering |

### Dev

| Package | Role |
|---------|------|
| `typescript` | Types |
| `tailwindcss` + `@tailwindcss/postcss` | Styles |
| `eslint` + `eslint-config-next` | Lint |
| `vitest` + Testing Library + `jsdom` | Tests |

---

## 4. External services (not pip/npm)

Needed to see the features built in this workstream:

| Service | Env vars | Feature |
|---------|----------|---------|
| **PostgreSQL** | `DATABASE_URL` | All persisted data |
| **Resend** | `RESEND_API_KEY`, `MAIL_FROM` | Forgot-password email |
| **Google Cloud OAuth** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Continue with Google |
| DeepSeek / NVIDIA (optional) | `DEEPSEEK_API_KEY`, `NVIDIA_API_KEY` | Challenge / tutor LLM |
| Pixabay / YouTube (optional) | `PIXABAY_API_KEY`, `YOUTUBE_API_KEY` | Media (challenges use `local_only` by default) |

Also set: `SECRET_KEY`, `FRONTEND_URL`, `CORS_ORIGINS`, `ENVIRONMENT`.

Copy `smarttrack-backend/.env.example` → `.env` and fill values. **Never commit `.env`.**

---

## 5. Features ↔ what they need

| Feature | Depends on |
|---------|------------|
| Email / password login | Postgres, JWT libs, bcrypt |
| Forgot / reset password | Resend (+ domain later for any recipient), `password_resets` table, `FRONTEND_URL` |
| Google Sign-In | Google OAuth client + test users (Testing mode) |
| Course Directory | `data/course_directory.json` (no extra package) |
| Recommendations (behavioural ± WASSCE) | Postgres, cut-off JSON, optional sklearn model |
| Challenges + local images | LLM keys optional; `CHALLENGE_IMAGES_MODE=local_only` |
| Dashboard / Your path / progress | Postgres + existing frontend deps |

---

## 6. Run locally (after installs + `.env`)

```bash
# Terminal 1 — DB must be up, then:
cd smarttrack-backend
uvicorn app.main:app --reload
# → http://127.0.0.1:8000

# Terminal 2
cd smarttrack-frontend
npm run dev
# → http://localhost:3000
```

Point `FRONTEND_URL` and Google redirect at the same frontend origin  
(e.g. `http://localhost:3000`, callback `http://localhost:3000/auth/callback`).

---

## 7. Later (production / all student emails)

- Host frontend + backend (e.g. Vercel + Render)
- Set `ENVIRONMENT=production`, real `FRONTEND_URL`
- Verify a **custom domain** in Resend → update `MAIL_FROM`
- Add production Google redirect URIs; publish OAuth when ready
