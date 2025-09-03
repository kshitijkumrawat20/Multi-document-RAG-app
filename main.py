from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
from typing import Optional
import uuid
from datetime import datetime

from app.api.v1.routes import router as api_router
from app.core.session_manager import session_manager
from app.config.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="ClariDoc API",
    description="Professional Document Analysis & RAG Platform API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    try:
        # Test database connection
        session_manager.db.init_db()
        print("Database connection verified successfully")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "ClariDoc API", 
        "status": "running",
        "description": "Professional Document Analysis & RAG Platform"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    try:
        # Test database connection
        session_manager.db.init_db()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy", 
        "service": "ClariDoc FastAPI Backend",
        "database": db_status,
        "timestamp": datetime.now()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,  # Disable reload in production
        log_level="info"
    )