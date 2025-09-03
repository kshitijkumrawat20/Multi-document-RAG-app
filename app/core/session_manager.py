import uuid
from typing import Dict, Optional
from datetime  import datetime, timedelta
from app.services.RAG_service import RAGService
from app.database.database import SessionDatabase
from app.schemas.request_models import DocumentTypeSchema

class Session: ## session management 
    def __init__(self, session_id:str):
        self.session_id = session_id 
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.rag_service : Optional[RAGService] = None
        self.document_uploaded = False
        self.vector_store_created = False
        self.document_info = {}
        self.username = None

    def update_activity(self):
        self.last_activity = datetime.now()

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.db = SessionDatabase()

    def create_session(self, username: str = "anonymous") -> str:
        session_id  = str(uuid.uuid4())
        session = Session(session_id)
        session.username = username
        self.sessions[session_id] = session
        
        # Save to database
        self.db.create_session(session_id, username)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        # First check in-memory sessions
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired():
                session.update_activity()
                return session
            else:
                del self.sessions[session_id]
        
        # If not in memory, try to restore from database
        db_session = self.db.get_session(session_id)
        if db_session and db_session['is_active']:
            # Restore session to memory
            session = Session(session_id)
            session.username = db_session['username']
            session.document_uploaded = db_session['chunks_count'] > 0
            session.vector_store_created = db_session['pinecone_index'] is not None
            session.document_info = {
                'filename': db_session['document_name'],
                'type': db_session['document_type'],
                'chunks_count': db_session['chunks_count']
            }
            
            # Initialize RAG service if document exists (same as restore_session)
            if session.vector_store_created:
                print(f"[SessionManager] Restoring RAG service for session {session_id}")
                session.rag_service = RAGService()
                
                # Set the basic attributes
                session.rag_service.index = db_session['pinecone_index']
                session.rag_service.namespace = db_session['pinecone_namespace']
                session.rag_service.Document_path = db_session['document_path']
                session.rag_service.url = db_session['document_url']
                
                # Create a mock splitter with the keywords file path for restored sessions
                from app.ingestion.text_splitter import splitting_text
                from app.utils.metadata_utils import MetadataService
                
                # Recreate the document type information
                metadataservice = MetadataService()
                mock_scheme = DocumentTypeSchema(document_types="Insurance")  # Default for restored sessions
                document_type = metadataservice.Return_document_model(mock_scheme)
                session.rag_service.DocumentTypeScheme = mock_scheme
                session.rag_service.Document_Type = document_type
                
                # Create splitter instance to maintain the keywords file path
                session.rag_service.splitter = splitting_text(documentTypeSchema=document_type, llm=session.rag_service.llm)
                
                # Generate the expected keywords file path based on document name
                import os
                document_name = db_session['document_name'] or 'unknown'
                keywords_filename = document_name.replace(".", "").replace("\\", "").replace("/", "") + ".json"
                session.rag_service.splitter.Keywordsfile_path = os.path.join("app/data/", keywords_filename)
                
                print(f"[SessionManager] RAG service restored with index: {session.rag_service.index}")
            
            self.sessions[session_id] = session
            return session
        
        return None
    
    def update_session_document(self, session_id: str, document_name: str, 
                               document_type: str, chunks_count: int,
                               pinecone_index: str = None, pinecone_namespace: str = None,
                               document_path: str = None, document_url: str = None):
        """Update session with document information"""
        self.db.update_session(
            session_id,
            document_name=document_name,
            document_type=document_type,
            chunks_count=chunks_count,
            pinecone_index=pinecone_index,
            pinecone_namespace=pinecone_namespace,
            document_path=document_path,
            document_url=document_url
        )
        
        # Update in-memory session if exists
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.document_uploaded = True
            session.vector_store_created = pinecone_index is not None
            session.document_info = {
                'filename': document_name,
                'type': document_type,
                'chunks_count': chunks_count
            }
    
    def get_user_sessions(self, username: str):
        """Get all sessions for a user"""
        return self.db.get_user_sessions(username)
    
    def restore_session(self, session_id: str) -> bool:
        """Restore a session from database"""
        db_session = self.db.get_session(session_id)
        if db_session and db_session['is_active']:
            session = Session(session_id)
            session.username = db_session['username']
            session.document_uploaded = db_session['chunks_count'] > 0
            session.vector_store_created = db_session['pinecone_index'] is not None
            session.document_info = {
                'filename': db_session['document_name'],
                'type': db_session['document_type'],
                'chunks_count': db_session['chunks_count']
            }
            
            # Initialize RAG service if document exists
            if session.vector_store_created:
                print(f"[SessionManager] Restoring RAG service for session {session_id}")
                session.rag_service = RAGService()
                
                # Set the basic attributes
                session.rag_service.index = db_session['pinecone_index']
                session.rag_service.namespace = db_session['pinecone_namespace']
                session.rag_service.Document_path = db_session['document_path']
                session.rag_service.url = db_session['document_url']
                
                # Create a mock splitter with the keywords file path for restored sessions
                from app.ingestion.text_splitter import splitting_text
                from app.utils.metadata_utils import MetadataService
                
                # Recreate the document type information
                metadataservice = MetadataService()
                mock_scheme = DocumentTypeSchema(document_types="Insurance")  # Default for restored sessions
                document_type = metadataservice.Return_document_model(mock_scheme)
                session.rag_service.DocumentTypeScheme = mock_scheme
                session.rag_service.Document_Type = document_type
                
                # Create splitter instance to maintain the keywords file path
                session.rag_service.splitter = splitting_text(documentTypeSchema=document_type, llm=session.rag_service.llm)
                
                # Generate the expected keywords file path based on document name
                import os
                document_name = db_session['document_name'] or 'unknown'
                keywords_filename = document_name.replace(".", "").replace("\\", "").replace("/", "") + ".json"
                session.rag_service.splitter.Keywordsfile_path = os.path.join("app/data/", keywords_filename)
                
                print(f"[SessionManager] RAG service restored with index: {session.rag_service.index}")
            
            self.sessions[session_id] = session
            return True
        return False
    
    def delete_session(self, session_id:str): 
        if session_id in self.sessions:
            del self.sessions[session_id]
        self.db.deactivate_session(session_id)
    
    def cleanup_expired_sessions(self): 
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        for sid in expired_sessions:
            del self.sessions[sid]

session_manager = SessionManager()

