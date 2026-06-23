# Atlas Backend 🐍

Python FastAPI backend for the Atlas AI-powered career guidance platform.

## Stack
- **Framework**: FastAPI + Uvicorn  
- **Database**: PostgreSQL on [Neon](https://neon.tech) (serverless)
- **ORM**: SQLAlchemy 2.0 (async) + Alembic migrations
- **Auth**: JWT (access + refresh tokens) + Google OAuth 2.0
- **Deploy**: Render (free tier)

## Project Structure

```
atlas-backend/
├── app/
│   ├── main.py              # FastAPI entry, CORS, router registration
│   ├── config.py            # Settings from .env
│   ├── database.py          # Async SQLAlchemy engine + get_db dependency
│   ├── auth/
│   │   ├── router.py        # /api/v1/auth/* routes
│   │   ├── service.py       # Hashing, JWT, refresh tokens, Google OAuth
│   │   ├── schemas.py       # Request/Response Pydantic models
│   │   └── dependencies.py  # get_current_user bearer dependency
│   └── users/
│       ├── models.py        # User + RefreshToken ORM models
│       ├── schemas.py       # UserPublic, UserUpdate
│       └── router.py        # /api/v1/users/* routes
├── alembic/                 # DB migrations
├── alembic.ini
├── Dockerfile
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | ❌ | Create account |
| POST | `/api/v1/auth/login` | ❌ | Login |
| POST | `/api/v1/auth/refresh` | ❌ | Refresh access token |
| POST | `/api/v1/auth/logout` | ❌ | Revoke refresh token |
| GET | `/api/v1/auth/google/url` | ❌ | Get Google consent URL |
| POST | `/api/v1/auth/google/callback` | ❌ | Exchange Google code |
| GET | `/api/v1/auth/me` | ✅ | Who am I |
| GET | `/api/v1/users/me` | ✅ | Get profile |
| PATCH | `/api/v1/users/me` | ✅ | Update profile |
| GET | `/health` | ❌ | Health check |

Interactive docs: `http://localhost:8000/docs` (dev mode only)

## Setup

### 1. Create & activate virtual environment
```bash
cd atlas-backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
# Copy the template and fill in your values
cp .env.example .env
```

Fill in `.env`:
- `DATABASE_URL` → from [Neon dashboard](https://neon.tech) → your project → Connection string (use `postgresql+asyncpg://...`)
- `SECRET_KEY` → run `python -c "import secrets; print(secrets.token_hex(32))"`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` → from [Google Cloud Console](https://console.cloud.google.com/)

### 4. Run database migrations
```bash
# Generate initial migration from models
alembic revision --autogenerate -m "initial"

# Apply to database
alembic upgrade head
```

### 5. Start the dev server
```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

## Deployment (Render)

1. Push `atlas-backend/` to GitHub as its own repo (or a subfolder)
2. Create new **Web Service** on Render → connect repo
3. Set **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Add all `.env` values as **Environment Variables** in Render dashboard
5. Set `CORS_ORIGINS` to your Vercel frontend URL

## Connecting to Next.js Frontend

In your Next.js app, set:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000    # dev
NEXT_PUBLIC_API_URL=https://your-api.onrender.com  # prod
```

Then call it like:
```typescript
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```
