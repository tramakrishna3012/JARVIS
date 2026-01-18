# JARVIS - AI Job Application & Referral Automation Platform

An end-to-end AI-powered automated job application platform that autonomously discovers jobs, generates tailored resumes, applies to positions, manages referrals, and handles email communications.

## 🏗️ Architecture

- **Frontend**: Next.js 14 (TypeScript) - Vercel optimized
- **Backend**: FastAPI (Python 3.11) - Serverless functions
- **Database**: PostgreSQL (Vercel Postgres)
- **Cache**: Redis (Upstash)
- **AI/LLM**: OpenAI GPT-4

## 📁 Project Structure

```
JARVIS/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, security
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── agents/      # AI orchestration
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # App router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   └── package.json
└── vercel.json
```

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Environment Variables

Create `.env` files in both `backend/` and `frontend/`:

### Backend (.env)
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
OPENAI_API_KEY=sk-...
JWT_SECRET=your-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Security

- JWT authentication with refresh tokens
- OAuth 2.0 for LinkedIn integration
- bcrypt password hashing
- Rate limiting on all endpoints
- Full audit logging

## 📄 License

MIT
