from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import os 
import tempfile
from pathlib import Path
from app.core.session_manager import SessionManager, Session
from app.services.RAG_service import RAGService
from app.schemas.request_models import QueryRequest
from app.schemas.response_models import SessionResponse, QueryResponse,UploadResponse
from app.config.config import get_settings

router = APIRouter()

def get_session(session_id:str) -> Session:
    """"""