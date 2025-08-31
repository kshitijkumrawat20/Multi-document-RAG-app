from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SourceDocument(BaseModel):
    doc_id: str
    page: int
    text: str
    score: float
    metadata: Dict[str, Any]

class QueryResponse(BaseModel): 
    session_id: str 
    query: str
    answer: str
    query_metadata: Optional[Dict[str, Any]] = None
    sources: Optional[List[SourceDocument]] = None
    message: str

class SessionResponse(BaseModel):
    session_id: str
    message: str 

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    document_type: str
    chunks_created: int 
    message: str 

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None