import streamlit as st
import requests
import json
from typing import Optional, List, Dict
import time
import os
import magic  # For file type detection

# Configuration
# API_BASE_URL = "http://localhost:8000/api/v1"
API_BASE_URL = "https://kshitijk20-claridoc.hf.space/api/v1"

# Professional theme colors for ClariDoc
THEME_COLORS = {
    "primary": "#1E3A8A",      # Deep blue
    "secondary": "#3B82F6",    # Blue
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Amber
    "error": "#EF4444",        # Red
    "neutral": "#6B7280",      # Gray
    "light": "#2F89E3"         # Light gray
}

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
    
    def query_document(self, query: str) -> Optional[Dict]:
        """Query the uploaded document and return full response data"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/query/{self.session_id}",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
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

def show_professional_header():
    """Display professional ClariDoc header"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📄 ClariDoc
        </h1>
        <p style="color: #E5E7EB; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Professional Document Analysis & RAG Platform
        </p>
        <p style="color: #D1D5DB; text-align: center; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            HR • Insurance • Legal • Financial • Government • Technical Policies
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_login_form():
    """Show professional login form"""
    show_professional_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: #1E293B; padding: 2rem; border-radius: 10px; border: 1px solid #374151;">
            <h3 style="text-align: center; color: #60A5FA; margin-bottom: 1.5rem;">
                🔐 Welcome to ClariDoc
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown('<p style="color: #E2E8F0; font-size: 1.1rem; font-weight: 600;">Enter your credentials to continue</p>', unsafe_allow_html=True)
            username = st.text_input(
                "Username", 
                value="professional_user", 
                help="Enter your username to access your document sessions",
                placeholder="e.g., john.doe@company.com"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                cancel = st.form_submit_button("Cancel", type="secondary")
            with col_b:
                submit = st.form_submit_button("Login", type="primary")
            
            if submit and username:
                st.session_state.username = username
                st.session_state.logged_in = True
                st.rerun()

def show_document_type_indicator(doc_type: str):
    """Show document type with appropriate icon and color"""
    type_config = {
        "HR/Employment": {"icon": "👥", "color": "#10B981"},
        "Insurance": {"icon": "🛡️", "color": "#3B82F6"},
        "Legal/Compliance": {"icon": "⚖️", "color": "#8B5CF6"},
        "Financial/Regulatory": {"icon": "💰", "color": "#F59E0B"},
        "Government/Public Policy": {"icon": "🏛️", "color": "#EF4444"},
        "Technical/IT Policies": {"icon": "⚙️", "color": "#6B7280"}
    }
    
    config = type_config.get(doc_type, {"icon": "📄", "color": "#6B7280"})
    
    st.markdown(f"""
    <div style="display: inline-block; background: {config['color']}20; color: {config['color']}; 
         padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600; margin: 0.25rem 0;">
        {config['icon']} {doc_type}
    </div>
    """, unsafe_allow_html=True)

def show_session_selector(app: RAGApp):
    """Show professional session selection interface"""
    st.sidebar.markdown("### 📂 Document Sessions")
    
    # Get user sessions
    sessions = app.get_user_sessions()
    
    if sessions:
        st.sidebar.markdown("#### Active Sessions")
        for i, session in enumerate(sessions):
            with st.sidebar.container():
                session_label = session['document_name'] or 'Untitled Document'
                
                # Create a clean session card
                st.markdown(f"""
                <div style="background: #1E293B; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #3B82F6; border: 1px solid #374151;">
                    <div style="font-weight: 600; color: #60A5FA;">{session_label}</div>
                    <div style="font-size: 0.8rem; color: #94A3B8;">
                        📄 {session['document_type']} • {session['chunks_count']} chunks
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8;">
                        🕐 {session['last_accessed']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.sidebar.button("🔄 Restore", key=f"restore_{session['session_id']}", help="Restore this session"):
                    if app.restore_session(session['session_id']):
                        st.success(f"✅ Restored: {session_label}")
                        st.rerun()
                
                st.sidebar.divider()
    
    # Create new session button
    if st.sidebar.button("➕ New Session", type="primary", use_container_width=True):
        if app.create_session():
            st.success("🎉 New session created!")
            st.rerun()

def show_query_metadata(metadata: Dict):
    """Display extracted query metadata in a professional format"""
    if not metadata:
        return
        
    st.markdown('<h4 style="color: #E2E8F0;">🔍 Query Analysis</h4>', unsafe_allow_html=True)
    
    with st.expander("📊 Extracted Metadata", expanded=True):
        # Filter out None values and empty lists
        filtered_metadata = {k: v for k, v in metadata.items() 
                           if v is not None and v != [] and v != {}}
        
        if filtered_metadata:
            cols = st.columns(2)
            col_idx = 0
            
            for key, value in filtered_metadata.items():
                with cols[col_idx % 2]:
                    # Format the key nicely
                    display_key = key.replace('_', ' ').title()
                    
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value[:3])  # Show first 3 items
                        if len(value) > 3:
                            value_str += f" (+{len(value)-3} more)"
                    else:
                        value_str = str(value)
                    
                    st.markdown(f"""
                    <div style="background: #1E293B; padding: 0.75rem; border-radius: 6px; margin: 0.25rem 0; border: 1px solid #374151;">
                        <div style="font-weight: 600; color: #60A5FA; font-size: 0.9rem;">{display_key}</div>
                        <div style="color: #E2E8F0; font-size: 0.8rem; margin-top: 0.25rem;">{value_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                col_idx += 1
        else:
            st.info("ℹ️ No specific metadata extracted from this query")

def show_document_sources(top_clauses: List[Dict]):
    """Display top document sources with metadata"""
    if not top_clauses:
        return
        
    st.markdown('<h4 style="color: #E2E8F0;">📚 Source Documents</h4>', unsafe_allow_html=True)
    
    for i, clause in enumerate(top_clauses[:3]):  # Show top 3
        metadata = clause.get('metadata', {})
        
        # Extract key information
        doc_id = metadata.get('doc_id', 'Unknown')[:8] + '...'
        page_num = metadata.get('page_no', metadata.get('page', 'N/A'))
        score = clause.get('score', 0)
        
        # Get relevant metadata (skip technical fields)
        skip_fields = {'doc_id', 'chunk_id', 'source', 'file_path', 'type', 'author', 'creator', 'producer','doc_category','format','keyword', 'doc_type','modDate','moddate','subject','title','total_pages','trapped','creationDate','creationdate' }
        relevant_metadata = {k: v for k, v in metadata.items() 
                           if k not in skip_fields and v is not None and v != [] and v != ''}
        
        with st.expander(f"📄 Document {i+1} (Page {page_num}) - Relevance: {score:.3f}", expanded=i==0):
            # Show the text content
            text_content = clause.get('text', '')
            if text_content:
                st.markdown('<p style="color: #E2E8F0; font-weight: 600;">📝 Content:</p>', unsafe_allow_html=True)
                st.markdown(f'<div style="background: #1E293B; padding: 1rem; border-radius: 6px; border-left: 3px solid #3B82F6; font-style: italic; border: 1px solid #374151; color: #E2E8F0;">{text_content[:300]}{"..." if len(text_content) > 300 else ""}</div>', 
                           unsafe_allow_html=True)
            
            # Show metadata in a clean format
            if relevant_metadata:
                st.markdown('<p style="color: #E2E8F0; font-weight: 600;">📊 Document Properties:</p>', unsafe_allow_html=True)
                
                # Create columns for metadata
                if len(relevant_metadata) <= 4:
                    cols = st.columns(len(relevant_metadata))
                else:
                    cols = st.columns(2)
                
                for idx, (key, value) in enumerate(relevant_metadata.items()):
                    col_idx = idx % len(cols)
                    with cols[col_idx]:
                        display_key = key.replace('_', ' ').title()
                        
                        if isinstance(value, list):
                            value_str = ", ".join(str(v) for v in value[:2])
                            if len(value) > 2:
                                value_str += f" (+{len(value)-2})"
                        else:
                            value_str = str(value)
                        
                        st.markdown(f"""
                        <div style="background: #451A03; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0; border: 1px solid #78350F;">
                            <div style="font-weight: 600; color: #FCD34D; font-size: 0.8rem;">{display_key}</div>
                            <div style="color: #FEF3C7; font-size: 0.75rem;">{value_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Technical details in a collapsed section
            with st.expander("🔧 Technical Details", expanded=False):
                st.code(f"""
Document ID: {doc_id}
Page Number: {page_num}
Relevance Score: {score:.4f}
Source: {metadata.get('source', 'N/A')}
                """)

def main():
    st.set_page_config(
        page_title="ClariDoc - Professional Document Analysis",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional dark styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
    }
    .stSidebar {
        background-color: #1E293B;
        color: #E2E8F0;
    }
    .stButton > button {
        border-radius: 6px;
        border: none;
        font-weight: 600;
        background-color: #3B82F6;
        color: white;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .stSelectbox > div > div {
        border-radius: 6px;
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
    }
    .stTextInput > div > div > input {
        border-radius: 6px;
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
    }
    .stFileUploader {
        border-radius: 6px;
        background-color: #1E293B;
        color: #E2E8F0;
    }
    .stFileUploader > div {
        background-color: #1E293B;
        color: #E2E8F0;
    }
    .stRadio > div {
        background-color: transparent;
        color: #E2E8F0;
    }
    .stCheckbox > div {
        color: #E2E8F0;
    }
    /* Dark theme for expanders and metrics */
    .stExpander {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
        border: 1px solid #374151 !important;
    }
    .stExpander > div {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
    }
    .stExpander summary {
        color: #E2E8F0 !important;
    }
    .stMetric {
        background-color: #1E293B !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid #374151 !important;
        color: #E2E8F0 !important;
    }
    .stMetric > div {
        color: #E2E8F0 !important;
    }
    .stMetric label {
        color: #94A3B8 !important;
    }
    .stMetric [data-testid="metric-value"] {
        color: #E2E8F0 !important;
    }
    /* Chat message styling */
    .stChatMessage {
        background-color: #1E293B;
        color: #E2E8F0;
    }
    /* Form styling */
    .stForm {
        background-color: #1E293B;
        border: 1px solid #374151;
        border-radius: 8px;
    }
    /* Info/success/error boxes */
    .stAlert {
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
    }
    /* Sidebar elements */
    .sidebar .element-container {
        color: #E2E8F0;
    }
    /* Progress bar */
    .stProgress > div > div {
        background-color: #3B82F6;
    }
    /* All text elements */
    p, h1, h2, h3, h4, h5, h6, span, div {
        color: #E2E8F0 !important;
    }
    /* Markdown content */
    .stMarkdown {
        color: #E2E8F0;
    }
    /* Code blocks */
    .stCode {
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = "professional_user"
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Show login form if not logged in
    if not st.session_state.logged_in:
        show_login_form()
        return
    
    # Show professional header
    show_professional_header()
    
    # Initialize app
    if 'app' not in st.session_state:
        st.session_state.app = RAGApp()
    
    app = st.session_state.app
    app.set_username(st.session_state.username)
    
    # Restore session ID if it exists in session state
    if hasattr(st.session_state, 'session_id') and st.session_state.session_id:
        app.session_id = st.session_state.session_id
    
    # Welcome message
    st.markdown(f"""
    <div style="background: #134E4A; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #10B981;">
        <h4 style="color: #6EE7B7; margin: 0;">👋 Welcome back, <strong>{st.session_state.username}</strong>!</h4>
        <p style="color: #A7F3D0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Ready to analyze your professional documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session management in sidebar
    show_session_selector(app)
    
    # Logout button in sidebar
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = "professional_user"
        st.session_state.clear()
        st.rerun()
    
    # Main content area
    if not app.session_id:
        st.info("👈 Please create or select a session from the sidebar to begin document analysis")
        return
    
    # Display current session info
    st.success(f"🎯 **Active Session:** `{app.session_id[:8]}...`")
    
    # Document upload section
    st.markdown("---")
    st.markdown('<h2 style="color: #E2E8F0;">📤 Document Upload</h2>', unsafe_allow_html=True)
    
    # Upload type selection
    upload_type = st.radio(
        "📂 Choose upload method:",
        ["📁 File Upload", "🌐 URL Import"],
        horizontal=True
    )
    
    col1, col2 = st.columns([3, 1])
    
    if upload_type == "📁 File Upload":
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a professional document",
                type=['pdf', 'docx', 'doc'],
                help="Upload PDF or Word documents for analysis"
            )
        
        with col2:
            auto_detect = st.checkbox("🔍 Auto-detect type", value=True)
            if not auto_detect:
                doc_type = st.selectbox("Document Type", ["pdf", "word"])
            else:
                doc_type = None
        
        if uploaded_file and st.button("🚀 Upload & Process", type="primary"):
            with st.spinner("🔄 Processing document..."):
                progress_bar = st.progress(0)
                progress_bar.progress(25, "📄 Analyzing document structure...")
                time.sleep(0.5)
                progress_bar.progress(50, "🧠 Extracting metadata...")
                time.sleep(0.5)
                progress_bar.progress(75, "🔗 Creating vector embeddings...")
                time.sleep(0.5)
                
                if app.upload_document(file=uploaded_file, doc_type=doc_type):
                    progress_bar.progress(100, "✅ Document processed successfully!")
                    st.balloons()
                    time.sleep(1)
                    progress_bar.empty()
    
    else:  # URL Upload
        with col1:
            url = st.text_input(
                "📎 Enter document URL:",
                placeholder="https://example.com/document.pdf",
                help="Enter a direct URL to a PDF document"
            )
        
        with col2:
            doc_type = st.selectbox("Document Type", ["pdf", "word"], index=0)
        
        if url and st.button("🚀 Load from URL & Process", type="primary"):
            with st.spinner("🔄 Processing document from URL..."):
                progress_bar = st.progress(0)
                progress_bar.progress(20, "🌐 Downloading document...")
                time.sleep(0.5)
                progress_bar.progress(50, "📄 Analyzing document structure...")
                time.sleep(0.5)
                progress_bar.progress(80, "🧠 Extracting metadata...")
                time.sleep(0.5)
                
                if app.upload_document(url=url, doc_type=doc_type):
                    progress_bar.progress(100, "✅ Document processed successfully!")
                    st.balloons()
                    time.sleep(1)
                    progress_bar.empty()
    
    # Query section
    st.markdown("---")
    st.markdown('<h2 style="color: #E2E8F0;">💬 Document Analysis</h2>', unsafe_allow_html=True)
    
    # Display session status
    status = app.get_session_status()
    if status and status.get("document_uploaded"):
        doc_info = status.get("document_info", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Document", doc_info.get('filename', 'Unknown'))
        with col2:
            st.metric("🧩 Chunks", doc_info.get('chunks_count', 0))
        with col3:
            st.metric("📊 Type", doc_info.get('type', 'Unknown'))
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "metadata" in message:
                # Show the answer
                st.markdown(message["content"])
                
                # Show metadata and sources
                if message.get("metadata"):
                    show_query_metadata(message["metadata"])
                
                if message.get("sources"):
                    show_document_sources(message["sources"])
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💭 Ask a question about your document..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                progress_bar = st.progress(0)
                progress_bar.progress(25, "🔍 Extracting query metadata...")
                time.sleep(0.3)
                progress_bar.progress(50, "🔎 Searching document database...")
                time.sleep(0.3)
                progress_bar.progress(75, "🧠 Generating response...")
                time.sleep(0.3)
                
                response_data = app.query_document(prompt)
                progress_bar.progress(100, "✅ Analysis complete!")
                time.sleep(0.5)
                progress_bar.empty()
                
                if response_data:
                    answer = response_data.get("answer", "No answer available")
                    st.markdown(answer)
                    
                    # Extract and display metadata
                    query_metadata = response_data.get("query_metadata", {})
                    sources = response_data.get("sources", [])
                    
                    if query_metadata:
                        show_query_metadata(query_metadata)
                    
                    if sources:
                        show_document_sources(sources)
                    
                    # Add to chat history with metadata
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "metadata": query_metadata,
                        "sources": sources
                    })
                else:
                    error_msg = "❌ Sorry, I couldn't process your question."
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.session_state.messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Conversation", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

if __name__ == "__main__":
    main()