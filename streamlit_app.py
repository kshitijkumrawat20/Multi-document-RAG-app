import streamlit as st
import requests
import json
from typing import Optional, List, Dict
import time
import os
import magic  # For file type detection

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

class RAGApp:
    def __init__(self):
        self.session_id: Optional[str] = None
        self.username: str = "anonymous"
        
    def set_username(self, username: str):
        """Set the username for the app"""
        self.username = username
        
    def create_session(self) -> bool:
        """Create a new session with the API"""
        try:
            response = requests.post(f"{API_BASE_URL}/session", params={"username": self.username})
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                st.session_state.session_id = self.session_id
                return True
        except Exception as e:
            st.error(f"Failed to create session: {e}")
        return False
    
    def get_user_sessions(self) -> List[Dict]:
        """Get all sessions for current user"""
        try:
            response = requests.get(f"{API_BASE_URL}/sessions/{self.username}")
            if response.status_code == 200:
                data = response.json()
                return data.get("sessions", [])
        except Exception as e:
            st.error(f"Failed to get user sessions: {e}")
        return []
    
    def restore_session(self, session_id: str) -> bool:
        """Restore a session from database"""
        try:
            response = requests.post(f"{API_BASE_URL}/session/{session_id}/restore")
            if response.status_code == 200:
                self.session_id = session_id
                st.session_state.session_id = session_id
                return True
        except Exception as e:
            st.error(f"Failed to restore session: {e}")
        return False
    
    def detect_file_type(self, file_content: bytes, filename: str) -> str:
        """Detect file type from content and filename"""
        # Try to detect from filename extension first
        if filename.lower().endswith('.pdf'):
            return 'pdf'
        elif filename.lower().endswith(('.doc', '.docx')):
            return 'word'
        else:
            # Try to detect from file content using python-magic
            try:
                file_type = magic.from_buffer(file_content, mime=True)
                if 'pdf' in file_type:
                    return 'pdf'
                elif any(word_type in file_type for word_type in ['word', 'msword', 'document']):
                    return 'word'
            except:
                pass
        return 'unknown'
    
    def upload_document(self, file=None, url=None, doc_type=None) -> bool:
        """Upload document to the API (file or URL)"""
        try:
            if file:
                # Auto-detect file type if not provided
                if not doc_type:
                    file_content = file.getvalue()
                    doc_type = self.detect_file_type(file_content, file.name)
                    if doc_type == 'unknown':
                        st.error("Could not detect file type. Please specify manually.")
                        return False
                
                files = {"file": (file.name, file.getvalue(), file.type)}
                data = {"doc_type": doc_type}
                
                response = requests.post(
                    f"{API_BASE_URL}/upload/{self.session_id}",
                    files=files,
                    data=data
                )
            else:
                # URL upload
                data = {"url": url, "doc_type": doc_type or "pdf"}
                response = requests.post(
                    f"{API_BASE_URL}/upload/{self.session_id}",
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Document uploaded successfully! Created {result['chunks_created']} chunks.")
                return True
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response.text else f"HTTP {response.status_code}"
                st.error(f"Upload failed: {error_msg}")
                
        except Exception as e:
            st.error(f"Upload error: {e}")
        return False
    
    def query_document(self, query: str) -> Optional[str]:
        """Query the uploaded document"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/query/{self.session_id}",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["answer"]
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"Query failed: {error_detail}")
                
        except Exception as e:
            st.error(f"Query error: {e}")
        return None
    
    def get_session_status(self) -> Optional[dict]:
        """Get current session status"""
        try:
            response = requests.get(f"{API_BASE_URL}/session/{self.session_id}/status")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Status check error: {e}")
        return None

def show_login_form():
    """Show login/username form"""
    st.title("🔐 Welcome to RAG Document Analysis")
    st.markdown("Enter your username to continue with your sessions")
    
    with st.form("login_form"):
        username = st.text_input("Username", value="anonymous", help="Enter your username to access your sessions")
        submit = st.form_submit_button("Login")
        
        if submit and username:
            st.session_state.username = username
            st.session_state.logged_in = True
            st.rerun()

def show_session_selector(app: RAGApp):
    """Show session selection interface"""
    st.sidebar.header("📂 Your Sessions")
    
    # Get user sessions
    sessions = app.get_user_sessions()
    
    if sessions:
        st.sidebar.subheader("Existing Sessions")
        for session in sessions:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                session_label = f"{session['document_name'] or 'Untitled'} ({session['document_type']})"
                st.sidebar.text(session_label)
                st.sidebar.caption(f"Chunks: {session['chunks_count']} | {session['last_accessed']}")
            with col2:
                if st.sidebar.button("🔄", key=f"restore_{session['session_id']}", help="Restore this session"):
                    if app.restore_session(session['session_id']):
                        st.success(f"Restored session: {session_label}")
                        st.rerun()
    
    st.sidebar.divider()
    
    # Create new session button
    if st.sidebar.button("➕ Create New Session", type="primary"):
        if app.create_session():
            st.success("New session created!")
            st.rerun()

def main():
    st.set_page_config(
        page_title="RAG Document Analysis",
        page_icon="📄",
        layout="wide"
    )
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = "anonymous"
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Show login form if not logged in
    if not st.session_state.logged_in:
        show_login_form()
        return
    
    # Initialize app
    if 'app' not in st.session_state:
        st.session_state.app = RAGApp()
    
    app = st.session_state.app
    app.set_username(st.session_state.username)
    
    # Restore session ID if it exists in session state
    if hasattr(st.session_state, 'session_id') and st.session_state.session_id:
        app.session_id = st.session_state.session_id
    
    st.title("📄 RAG Document Analysis System")
    st.markdown(f"Welcome back, **{st.session_state.username}**!")
    
    # Session management in sidebar
    show_session_selector(app)
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = "anonymous"
        st.session_state.clear()
        st.rerun()
    
    # Main content area
    if not app.session_id:
        st.info("👈 Please create or select a session from the sidebar")
        return
    
    # Display current session info
    st.success(f"Active Session: {app.session_id[:8]}...")
    
    # Document upload section
    st.header("📤 Document Upload")
    
    # Upload type selection
    upload_type = st.radio(
        "Choose upload method:",
        ["File Upload", "URL"],
        horizontal=True
    )
    
    col1, col2 = st.columns([3, 1])
    
    if upload_type == "File Upload":
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a document",
                type=['pdf', 'docx', 'doc'],
                help="Upload PDF or Word documents"
            )
        
        with col2:
            auto_detect = st.checkbox("Auto-detect type", value=True)
            if not auto_detect:
                doc_type = st.selectbox("Document Type", ["pdf", "word"])
            else:
                doc_type = None
        
        if uploaded_file and st.button("🚀 Upload & Process"):
            with st.spinner("Processing document..."):
                if app.upload_document(file=uploaded_file, doc_type=doc_type):
                    st.balloons()
    
    else:  # URL Upload
        with col1:
            url = st.text_input(
                "Enter document URL:",
                placeholder="https://example.com/document.pdf",
                help="Enter a direct URL to a PDF document"
            )
        
        with col2:
            doc_type = st.selectbox("Document Type", ["pdf", "word"], index=0)
        
        if url and st.button("🚀 Load from URL & Process"):
            with st.spinner("Processing document from URL..."):
                if app.upload_document(url=url, doc_type=doc_type):
                    st.balloons()
    
    # Query section
    st.header("💬 Ask Questions")
    
    # Display session status
    status = app.get_session_status()
    if status and status.get("document_uploaded"):
        doc_info = status.get("document_info", {})
        st.info(f"📄 Document loaded: **{doc_info.get('filename', 'Unknown')}** ({doc_info.get('chunks_count', 0)} chunks)")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = app.query_document(prompt)
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_msg = "Sorry, I couldn't process your question."
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.session_state.messages and st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()