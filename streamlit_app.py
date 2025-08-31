import streamlit as st
import requests
import json
from typing import Optional
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

class RAGApp:
    def __init__(self):
        self.session_id: Optional[str] = None
        
    def create_session(self) -> bool:
        """Create a new session with the API"""
        try:
            response = requests.post(f"{API_BASE_URL}/session")
            print(f"[STREAMLIT DEBUG] Session creation response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                st.session_state.session_id = self.session_id
                print(f"[STREAMLIT DEBUG] Created session: {self.session_id}")
                return True
        except Exception as e:
            st.error(f"Failed to create session: {e}")
        return False
    
    def upload_document(self, file, doc_type: str) -> bool:
        """Upload document to the API"""
        try:
            print(f"[STREAMLIT DEBUG] Uploading with session: {self.session_id}")
            files = {"file": (file.name, file.getvalue(), file.type)}
            data = {"doc_type": doc_type}
            
            upload_url = f"{API_BASE_URL}/upload/{self.session_id}"
            print(f"[STREAMLIT DEBUG] Upload URL: {upload_url}")
            
            response = requests.post(
                upload_url,
                files=files,
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

def main():
    st.set_page_config(
        page_title="RAG Document Analysis",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 RAG Document Analysis System")
    st.markdown("Upload your documents and ask questions about them!")
    
    # Initialize app
    if 'app' not in st.session_state:
        st.session_state.app = RAGApp()
    
    app = st.session_state.app
    
    # Restore session ID if it exists in session state
    if hasattr(st.session_state, 'session_id') and st.session_state.session_id:
        app.session_id = st.session_state.session_id
    
    # Sidebar for session management
    with st.sidebar:
        st.header("Session Management")
        
        # Create new session
        if st.button("🔄 Create New Session"):
            if app.create_session():
                st.success("New session created!")
                st.rerun()
        
        # Display current session
        if hasattr(st.session_state, 'session_id') and st.session_state.session_id:
            app.session_id = st.session_state.session_id
            st.success(f"Session: {app.session_id[:8]}...")
            
            # Show session status
            status = app.get_session_status()
            if status:
                st.json({
                    "Document Uploaded": status["document_uploaded"],
                    "Vector Store Created": status["vector_store_created"],
                    "Document Info": status["document_info"]
                })
        else:
            st.warning("No active session. Please create one.")
    
    # Main content area
    if not app.session_id:
        st.info("👈 Please create a session first using the sidebar")
        return
    
    # Document upload section
    st.header("📤 Document Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'doc'],
            help="Upload PDF or Word documents"
        )
    
    with col2:
        doc_type = st.selectbox(
            "Document Type",
            ["pdf", "word"],
            help="Select the type of document you're uploading"
        )
    
    if uploaded_file and st.button("🚀 Upload & Process"):
        with st.spinner("Processing document..."):
            if app.upload_document(uploaded_file, doc_type):
                st.balloons()
    
    # Query section
    st.header("💬 Ask Questions")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
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