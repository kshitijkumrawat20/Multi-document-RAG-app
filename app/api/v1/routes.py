from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import os 
import tempfile
from pathlib import Path
from app.core.session_manager import SessionManager, Session, session_manager
from app.services.RAG_service import RAGService
from app.schemas.request_models import QueryRequest
from app.schemas.response_models import SessionResponse, QueryResponse, UploadResponse, SourceDocument
from app.config.config import get_settings

router = APIRouter()

def get_session(session_id:str) -> Session:
    """Dependency to get and validare session"""
    print(f"[DEBUG] Looking for session: {session_id}")
    print(f"[DEBUG] Available sessions: {list(session_manager.sessions.keys())}")
    session = session_manager.get_session(session_id=session_id)
    if not session: 
        print(f"[DEBUG] Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found or expired"
        )
    print(f"[DEBUG] Session found: {session_id}")
    return session

@router.post("/session", response_model=SessionResponse)
async def create_session(username: str = "anonymous"):
    """Create a new session for document processing"""
    session_id = session_manager.create_session(username)
    print(f"[DEBUG] Created session: {session_id} for user: {username}")
    print(f"[DEBUG] Total sessions now: {len(session_manager.sessions)}")
    return SessionResponse(
        session_id=session_id,
        message="Session created successfully"
    )

@router.get("/sessions/{username}")
async def get_user_sessions(username: str):
    """Get all sessions for a user"""
    sessions = session_manager.get_user_sessions(username)
    return {"sessions": sessions}

@router.post("/session/{session_id}/restore")
async def restore_session(session_id: str):
    """Restore a session from database"""
    success = session_manager.restore_session(session_id)
    if success:
        return {"message": "Session restored successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found or inactive")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"message": "Session deleted successfully"}

@router.post("/upload/{session_id}", response_model=UploadResponse)
async def upload_document(
    session_id: str, 
    file: UploadFile = File(None),
    url: str = Form(None),
    doc_type: str = Form(None),
    session: Session = Depends(get_session)
):
    """Upload and process a document from file or URL"""
    settings = get_settings()
    
    # Validate input - either file or URL must be provided
    if not file and not url:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided")
    
    if file and url:
        raise HTTPException(status_code=400, detail="Provide either file or URL, not both")
    
    try:
        # Initialize RAG service for this session 
        session.rag_service = RAGService()
        
        document_name = ""
        document_path = None
        document_url = None
        
        if file:
            # Handle file upload
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in settings.allowed_file_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_file_types}"
                )
            
            # Auto-detect document type if not provided
            if not doc_type:
                doc_type = "pdf" if file_extension == ".pdf" else "word"
            
            # Validate file size
            content = await file.read()
            if len(content) > settings.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size too large. Maximum size: {settings.max_file_size} bytes"
                )
            
            # Create upload directory
            upload_dir = Path(settings.upload_dir)
            upload_dir.mkdir(exist_ok=True)
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            document_name = file.filename
            document_path = tmp_file_path
            
            # Load and split document from file
            session.rag_service.load_and_split_document(
                type=doc_type, 
                path=tmp_file_path
            )
            
        else:
            # Handle URL upload
            if not doc_type:
                doc_type = "pdf"  # Default for URLs
            
            document_name = url.split('/')[-1] or "URL Document"
            document_url = url
            
            # Load and split document from URL
            session.rag_service.load_and_split_document(
                type=doc_type, 
                url=url
            ) 

        # Create vector store 
        session.rag_service.create_vector_store()

        # Update session state 
        session.document_uploaded = True
        session.vector_store_created = True
        session.document_info = {
            "filename": document_name,
            "type": doc_type,
            "size": len(content) if file else 0,
            "chunks_count": len(session.rag_service.chunks)
        }
        
        # Update session in database
        session_manager.update_session_document(
            session_id=session_id,
            document_name=document_name,
            document_type=doc_type,
            chunks_count=len(session.rag_service.chunks),
            pinecone_index=str(session.rag_service.index),
            pinecone_namespace=session.rag_service.namespace,
            document_path=document_path,
            document_url=document_url
        )
        
        # Clean up temporary file if it exists
        if document_path:
            try:
                os.unlink(document_path)
            except:
                pass

        return UploadResponse(
            session_id=session_id,
            filename=document_name,
            document_type=doc_type,
            chunks_created=len(session.rag_service.chunks),
            message="Document uploaded and processed successfully"
        )
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'document_path' in locals() and document_path:
            try:
                os.unlink(document_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/query/{session_id}", response_model = QueryResponse)
async def query_document(
    session_id: str, 
    query_request: QueryRequest,
    session: Session = Depends(get_session)
):
    """Query the uploaded Document"""
    if not session.document_uploaded or not session.vector_store_created:
        raise HTTPException(
            status_code= 400,
            detail="No docuement uploaded or processed for this session"
        )
    try: 
        # create query embedding
        session.rag_service.create_query_embedding(query_request.query)

        # retrive relevant docs 
        session.rag_service.retrive_documents()

        # generate answer
        answer = session.rag_service.answer_query(query_request.query)
        
        # Extract query metadata and sources for UI
        query_metadata = getattr(session.rag_service, 'query_metadata', {})
        
        # Extract source documents from results
        sources = []
        if hasattr(session.rag_service, 'result') and session.rag_service.result:
            matches = session.rag_service.result.get('matches', [])
            for match in matches[:3]:  # Top 3 sources
                metadata = match.get('metadata', {})
                sources.append(SourceDocument(
                    doc_id=metadata.get('doc_id', match.get('id', '')),
                    page=metadata.get('page_no', metadata.get('page', 0)),
                    text=metadata.get('text', ''),
                    score=match.get('score', 0.0),
                    metadata=metadata
                ))

        return QueryResponse(
            session_id=session_id,
            query=query_request.query,
            answer=answer,
            query_metadata=query_metadata,
            sources=sources,
            message="Query processed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Get session status and information"""
    return {
        "session_id": session_id,
        "created_at": session.created_at,
        "last_activity": session.last_activity,
        "document_uploaded": session.document_uploaded,
        "vector_store_created": session.vector_store_created,
        "document_info": session.document_info
    }

    
    

