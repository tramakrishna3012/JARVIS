"""
JARVIS Backend - FastAPI Application
AI Job Application & Referral Automation Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, jobs, resumes, applications, referrals, emails, profiles
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="JARVIS API",
    description="AI Job Application & Referral Automation Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(referrals.router, prefix="/api/referrals", tags=["Referrals"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "JARVIS API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
