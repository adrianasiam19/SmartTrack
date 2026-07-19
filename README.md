SmartTrack - Project Overview & Installation Guide
SmartTrack is a full-stack web application featuring an AI-powered career guidance platform built with a modern tech stack. It's a monorepo containing both a FastAPI backend and Next.js frontend.

📋 Project Overview
What is SmartTrack?
SmartTrack is a comprehensive career guidance and tracking platform that leverages Google's Generative AI to provide personalized career insights and guidance. The project is structured as a monorepo with two main components:

Backend: FastAPI-based REST API with database, authentication, and AI integration
Frontend: Next.js React application with TypeScript, Tailwind CSS, and modern UI
Tech Stack
Backend:

Framework: FastAPI + Uvicorn
Database: PostgreSQL (on Neon - serverless)
ORM: SQLAlchemy 2.0 (async) + Alembic migrations
Authentication: JWT (access + refresh tokens) + Google OAuth 2.0
AI: Google Generative AI (Gemini)
Testing: Pytest
Frontend:

Framework: Next.js 15.5 (React 19)
Language: TypeScript
Styling: Tailwind CSS 4
UI Components: Lucide React, Framer Motion
Testing: Vitest + React Testing Library
🚀 Installation Guide for Windows PC
Prerequisites
Before starting, ensure you have these installed:

Python 3.9+ - Download here
Node.js 18+ - Download here
Git - Download here
PostgreSQL - Optional (we'll use Neon cloud database)
Step 1: Clone the Repository
bash
git clone https://github.com/adrianasiam19/SmartTrack.git
cd SmartTrack
🔧 Backend Setup (Python/FastAPI)
Step 2: Set Up Python Environment
Navigate to the backend directory and create a virtual environment:

bash
cd smarttrack-backend

# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# You should see (.venv) in your terminal prompt
Step 3: Install Backend Dependencies
bash
pip install -r requirements.txt
Step 4: Configure Environment Variables
bash
# Copy the example file
copy .env.example .env
Now edit the .env file with your settings:

env
# Database URL (get from Neon: https://neon.tech)
DATABASE_URL=postgresql+asyncpg://username:password@host/dbname

# Generate a secret key:
# Open Python and run: 
#   python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# CORS and Frontend URL
CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
Getting Database & OAuth Credentials:

Database (Neon PostgreSQL):

Go to https://neon.tech
Sign up and create a project
Copy the connection string and paste in DATABASE_URL
Google OAuth:

Go to https://console.cloud.google.com/
Create a new project
Enable Google OAuth 2.0
Create credentials (OAuth 2.0 Client ID)
Get your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
Step 5: Run Database Migrations
bash
# Create initial migration
alembic revision --autogenerate -m "initial"

# Apply migrations to database
alembic upgrade head
Step 6: Start the Backend Server
bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload

# Option 2: Using the run script
python run.py
The API will be available at: http://localhost:8000

Interactive docs: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
🎨 Frontend Setup (Next.js/React)
Step 7: Set Up Frontend
In a new terminal, navigate to the frontend:

bash
cd smarttrack-frontend

# Install dependencies
npm install
# or
yarn install
Step 8: Configure Frontend Environment
Create a .env.local file in smarttrack-frontend/:

env
# Point to your backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
Step 9: Start the Frontend Development Server
bash
npm run dev
# or
yarn dev
The frontend will be available at: http://localhost:3000

✅ Verify Everything Works
Backend running?

Visit: http://localhost:8000/docs
You should see the Swagger API documentation
Frontend running?

Visit: http://localhost:3000
You should see the SmartTrack application
Both communicating?

Try logging in or making an API request from the frontend
Check browser DevTools (F12) → Network tab for API calls
📝 Available API Endpoints
Method	Endpoint	Auth	Purpose
POST	/api/v1/auth/register	❌	Create account
POST	/api/v1/auth/login	❌	Login
POST	/api/v1/auth/refresh	❌	Refresh token
POST	/api/v1/auth/logout	❌	Logout
GET	/api/v1/auth/google/url	❌	Google OAuth URL
POST	/api/v1/auth/google/callback	❌	Google callback
GET	/api/v1/auth/me	✅	Current user
GET	/api/v1/users/me	✅	User profile
PATCH	/api/v1/users/me	✅	Update profile
GET	/health	❌	Health check
🐛 Troubleshooting
Issue	Solution
pip: command not found	Python not installed or not in PATH. Install Python and restart terminal.
Database connection failed	Check DATABASE_URL in .env, ensure Neon database is running
Port 8000/3000 already in use	Kill the process or use different port: uvicorn app.main:app --port 8001
Module not found errors	Run pip install -r requirements.txt (backend) or npm install (frontend)
CORS errors	Ensure CORS_ORIGINS in backend .env includes frontend URL
📂 Project Structure
Code
SmartTrack/
├── smarttrack-backend/        # FastAPI backend
│   ├── app/
│   │   ├── main.py           # Entry point
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   ├── auth/             # Authentication
│   │   └── users/            # User management
│   ├── alembic/              # Database migrations
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
├── smarttrack-frontend/       # Next.js frontend
│   ├── app/                  # App pages
│   ├── components/           # React components
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript config
└── README.md
🚀 Next Steps
Explore the backend API: Visit http://localhost:8000/docs
Build your frontend: Start adding features in smarttrack-frontend/app/
Customize the AI: Modify Gemini prompts in the backend
Deploy: Use Render (backend) and Vercel (frontend) for production
