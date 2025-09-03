import streamlit as st
import requests
import json
from typing import Optional, List, Dict
import time
import os
import magic  # For file type detection

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
# API_BASE_URL = "https://kshitijk20-claridoc.hf.space/api/v1"

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
    <div style="background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.75rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 1.4rem; font-weight: 700;">
            📄 ClariDoc
        </h1>
        <p style="color: #E5E7EB; text-align: center; margin: 0.125rem 0 0 0; font-size: 0.8rem;">
            Professional Document Analysis & RAG Platform
        </p>
        <p style="color: #D1D5DB; text-align: center; margin: 0.125rem 0 0 0; font-size: 0.7rem;">
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
        <div style="background: #1E293B; padding: 1rem; border-radius: 8px; border: 1px solid #374151;">
            <h3 style="text-align: center; color: #60A5FA; margin-bottom: 0.75rem; font-size: 1rem;">
                🔐 Welcome to ClariDoc
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown('<p style="color: #E2E8F0; font-size: 0.9rem; font-weight: 600;">Enter your credentials to continue</p>', unsafe_allow_html=True)
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

def show_document_library(app: RAGApp):
    """Show document library with better spacing"""
    st.sidebar.markdown("### � Document Library")
    st.sidebar.markdown("")  # Add spacing
    
    # Get user sessions
    sessions = app.get_user_sessions()
    
    if sessions:
        st.sidebar.markdown("#### 📄 Your Documents")
        st.sidebar.markdown("")  # Add spacing
        
        for i, session in enumerate(sessions):
            document_name = session['document_name'] or 'Untitled Document'
            doc_type = session['document_type'] or 'Unknown'
            
            # Clean document card with better spacing
            st.sidebar.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E293B, #334155); 
                       padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; 
                       border: 1px solid #475569; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                    <span style="font-size: 1rem; margin-right: 0.5rem;">📄</span>
                    <div style="font-weight: 700; color: #E2E8F0; font-size: 0.85rem; line-height: 1.2;">
                        {document_name[:25]}{"..." if len(document_name) > 25 else ""}
                    </div>
                </div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="background: #3B82F620; padding: 0.125rem 0.25rem; border-radius: 3px; color: #60A5FA;">
                        {doc_type[:10]}{"..." if len(doc_type) > 10 else ""}
                    </span>
                    <span style="margin-left: 0.25rem;">• {session['chunks_count']} chunks</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.sidebar.button(
                "� Open Chat", 
                key=f"open_{session['session_id']}", 
                help=f"Start chatting with {document_name}",
                use_container_width=True
            ):
                if app.restore_session(session['session_id']):
                    st.session_state.page = "chat"
                    st.session_state.current_document = document_name
                    st.rerun()
            
            st.sidebar.markdown("")  # Add spacing between documents
    
    else:
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; color: #94A3B8;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <div style="font-size: 0.9rem;">No documents yet</div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem;">Upload your first document to get started</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Upload new document button with better styling
    st.sidebar.markdown("---")
    st.sidebar.markdown("")  # Add spacing
    
    if st.sidebar.button(
        "📤 Upload New Document", 
        type="primary", 
        use_container_width=True,
        help="Upload a new document for analysis"
    ):
        st.session_state.page = "upload"
        if app.create_session():
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

def show_upload_page(app: RAGApp):
    """Dedicated upload page with clean interface"""
    # Header for upload page
    st.markdown("""
    <div style="background: linear-gradient(135deg, #059669, #10B981); 
                padding: 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">
            📤 Upload Document
        </h1>
        <p style="color: #D1FAE5; margin: 0.25rem 0 0 0; font-size: 0.8rem;">
            Upload your professional document for AI-powered analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload instructions
    st.markdown("""
    <div style="background: #1E293B; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid #475569;">
        <h3 style="color: #60A5FA; margin: 0 0 0.5rem 0; font-size: 0.95rem;">📋 Upload Instructions</h3>
        <div style="color: #94A3B8; line-height: 1.2; font-size: 0.75rem;">
            <p style="margin: 0.125rem 0;">• <strong>Formats:</strong> PDF, Word (.docx, .doc)</p>
            <p style="margin: 0.125rem 0;">• <strong>Size:</strong> Up to 10MB</p>
            <p style="margin: 0.125rem 0;">• <strong>Types:</strong> HR, Insurance, Legal, Financial, Government, Technical</p>
            <p style="margin: 0.125rem 0;">• <strong>Time:</strong> 30-60 seconds</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload options with better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: #1E293B; padding: 1rem; border-radius: 6px; border: 1px solid #475569; height: 100%;">
            <h4 style="color: #60A5FA; margin: 0 0 0.5rem 0; text-align: center; font-size: 0.9rem;">📁 Upload from Computer</h4>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'doc'],
            help="Select a document from your computer",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # Show file info
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            st.markdown(f"""
            <div style="background: #0F172A; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; border: 1px solid #374151;">
                <div style="color: #E2E8F0; font-weight: 600; font-size: 0.75rem;">📄 {uploaded_file.name}</div>
                <div style="color: #94A3B8; font-size: 0.7rem;">Size: {file_size:.2f} MB</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #1E293B; padding: 1rem; border-radius: 6px; border: 1px solid #475569; height: 100%;">
            <h4 style="color: #60A5FA; margin: 0 0 0.5rem 0; text-align: center; font-size: 0.9rem;">🌐 Import from URL</h4>
        """, unsafe_allow_html=True)
        
        url = st.text_input(
            "Document URL",
            placeholder="https://example.com/document.pdf",
            help="Enter a direct link to a PDF document",
            label_visibility="collapsed"
        )
        
        if url:
            st.markdown(f"""
            <div style="background: #0F172A; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; border: 1px solid #374151;">
                <div style="color: #E2E8F0; font-weight: 600; font-size: 0.75rem;">🌐 URL Document</div>
                <div style="color: #94A3B8; font-size: 0.7rem; word-break: break-all;">{url[:50]}...</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Processing options
    st.markdown("")  # Add spacing
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        auto_detect = st.checkbox("🔍 Auto-detect document type", value=True)
        if not auto_detect:
            doc_type = st.selectbox("Document Type", ["pdf", "word"], label_visibility="collapsed")
        else:
            doc_type = None
    
    # Upload button
    st.markdown("")  # Add spacing
    
    if uploaded_file or url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Upload & Process Document", type="primary", use_container_width=True):
                process_document_upload(app, uploaded_file, url, doc_type)
    
    # Back to library button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()

def process_document_upload(app: RAGApp, uploaded_file=None, url=None, doc_type=None):
    """Process document upload with enhanced progress tracking"""
    with st.container():
        st.markdown("""
        <div style="background: #1E293B; padding: 2rem; border-radius: 12px; border: 1px solid #475569; margin: 2rem 0;">
            <h4 style="color: #60A5FA; text-align: center; margin: 0 0 1.5rem 0;">⚡ Processing Document</h4>
        """, unsafe_allow_html=True)
        
        # Progress steps
        steps = [
            "📄 Analyzing document structure...",
            "🧠 Extracting metadata...",
            "🔍 Creating searchable chunks...",
            "🔗 Building vector embeddings...",
            "✅ Finalizing processing..."
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, step in enumerate(steps):
            progress = (i + 1) * 20
            progress_bar.progress(progress, step)
            status_text.markdown(f"<div style='text-align: center; color: #94A3B8;'>{step}</div>", unsafe_allow_html=True)
            time.sleep(0.8)  # Slower for better UX
        
        # Actual upload
        if uploaded_file:
            success = app.upload_document(file=uploaded_file, doc_type=doc_type)
        else:
            success = app.upload_document(url=url, doc_type=doc_type)
        
        if success:
            st.balloons()
            st.success("🎉 Document processed successfully!")
            time.sleep(2)
            
            # Get document name for the session
            status = app.get_session_status()
            if status and status.get("document_uploaded"):
                doc_info = status.get("document_info", {})
                st.session_state.current_document = doc_info.get('filename', 'Document')
            
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.error("❌ Failed to process document. Please try again.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_chat_page(app: RAGApp):
    """Dedicated chat page with clean interface"""
    current_doc = st.session_state.get('current_document', 'Document')
    
    # Chat header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #7C3AED, #A855F7); 
                padding: 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 1.3rem; font-weight: 700;">
            💬 Chat with {current_doc[:30]}{"..." if len(current_doc) > 30 else ""}
        </h1>
        <p style="color: #E9D5FF; margin: 0.25rem 0 0 0; font-size: 0.75rem;">
            Ask questions and get intelligent insights from your document
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Document info bar
    status = app.get_session_status()
    if status and status.get("document_uploaded"):
        doc_info = status.get("document_info", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Document", doc_info.get('filename', 'Unknown')[:15] + "...")
        with col2:
            st.metric("🧩 Chunks", doc_info.get('chunks_count', 0))
        with col3:
            st.metric("📊 Type", doc_info.get('type', 'Unknown')[:12] + "...")
        with col4:
            st.metric("🎯 Session", app.session_id[:8] + "..." if app.session_id else "N/A")
    
    st.markdown("---")
    
    # Chat messages with improved styling
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "metadata" in message:
                    # Show the answer
                    st.markdown(message["content"])
                    
                    # Show metadata and sources in expandable sections
                    if message.get("metadata"):
                        with st.expander("📊 Query Analysis", expanded=False):
                            show_query_metadata(message["metadata"])
                    
                    if message.get("sources"):
                        with st.expander("📚 Source Documents", expanded=False):
                            show_document_sources(message["sources"])
                else:
                    st.markdown(message["content"])
    
    # Chat input with suggestions
    st.markdown("")  # Add spacing
    
    # Sample questions
    if not st.session_state.messages:
        st.markdown("### 💡 Suggested Questions")
        suggestions = [
            "Key policies?",
            "Main points?",
            "Compliance?",
            "Stakeholders?",
            "Important dates?"
        ]
        
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i % len(cols)]:
                if st.button(suggestion, key=f"suggestion_{i}", help="Click to use this question"):
                    # Add the suggestion to chat
                    st.session_state.messages.append({"role": "user", "content": suggestion})
                    process_chat_query(app, suggestion)
                    st.rerun()
    
    # Chat input
    if prompt := st.chat_input("💭 Ask a question about your document..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        process_chat_query(app, prompt)
        st.rerun()
    
    # Chat controls
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📚 Back to Library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()
    
    with col3:
        if st.button("📤 Upload New Doc", type="primary", use_container_width=True):
            st.session_state.page = "upload"
            if app.create_session():
                st.rerun()

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

def process_chat_query(app: RAGApp, query: str):
    """Process chat query with loading animation"""
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Processing animation
            progress_steps = [
                "🔍 Understanding your question...",
                "🔎 Searching document...",
                "🧠 Generating response...",
                "✅ Almost ready..."
            ]
            
            progress_bar = st.progress(0)
            for i, step in enumerate(progress_steps):
                progress_bar.progress((i + 1) * 25, step)
                time.sleep(0.4)
            
            response_data = app.query_document(query)
            progress_bar.empty()
            
            if response_data:
                answer = response_data.get("answer", "No answer available")
                st.markdown(answer)
                
                # Extract metadata and sources
                query_metadata = response_data.get("query_metadata", {})
                sources = response_data.get("sources", [])
                
                # Show expandable sections for metadata and sources
                if query_metadata:
                    with st.expander("📊 Query Analysis", expanded=False):
                        show_query_metadata(query_metadata)
                
                if sources:
                    with st.expander("📚 Source Documents", expanded=False):
                        show_document_sources(sources)
                
                # Add to chat history with metadata
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "metadata": query_metadata,
                    "sources": sources
                })
            else:
                error_msg = "❌ Sorry, I couldn't process your question. Please try again."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

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
        padding-top: 0.5rem;
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
        border-radius: 4px;
        border: none;
        font-weight: 600;
        background-color: #3B82F6;
        color: white;
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .stSelectbox > div > div {
        border-radius: 4px;
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
        font-size: 0.8rem;
    }
    .stTextInput > div > div > input {
        border-radius: 4px;
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
        font-size: 0.8rem;
    }
    .stFileUploader {
        border-radius: 4px;
        background-color: #1E293B;
        color: #E2E8F0;
        font-size: 0.8rem;
    }
    .stFileUploader > div {
        background-color: #1E293B;
        color: #E2E8F0;
    }
    .stRadio > div {
        background-color: transparent;
        color: #E2E8F0;
        font-size: 0.8rem;
    }
    .stCheckbox > div {
        color: #E2E8F0;
        font-size: 0.8rem;
    }
    /* Dark theme for expanders and metrics */
    .stExpander {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
        border: 1px solid #374151 !important;
        font-size: 0.8rem;
    }
    .stExpander > div {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
    }
    .stExpander summary {
        color: #E2E8F0 !important;
        font-size: 0.8rem;
    }
    .stMetric {
        background-color: #1E293B !important;
        padding: 0.5rem !important;
        border-radius: 4px !important;
        border: 1px solid #374151 !important;
        color: #E2E8F0 !important;
    }
    .stMetric > div {
        color: #E2E8F0 !important;
    }
    .stMetric label {
        color: #94A3B8 !important;
        font-size: 0.7rem !important;
    }
    .stMetric [data-testid="metric-value"] {
        color: #E2E8F0 !important;
        font-size: 0.9rem !important;
    }
    /* Chat message styling */
    .stChatMessage {
        background-color: #1E293B;
        color: #E2E8F0;
        font-size: 0.8rem;
    }
    /* Form styling */
    .stForm {
        background-color: #1E293B;
        border: 1px solid #374151;
        border-radius: 4px;
    }
    /* Info/success/error boxes */
    .stAlert {
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #374151;
        font-size: 0.8rem;
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
        font-size: 0.75rem;
    }
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main > div {
            padding-top: 0.25rem;
        }
        .stButton > button {
            font-size: 0.75rem;
            padding: 0.3rem 0.6rem;
        }
        .stMetric {
            padding: 0.375rem !important;
        }
        .stMetric label {
            font-size: 0.65rem !important;
        }
        .stMetric [data-testid="metric-value"] {
            font-size: 0.8rem !important;
        }
    }
    /* Compact spacing */
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    .stColumns > div {
        gap: 0.5rem;
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
    if 'page' not in st.session_state:
        st.session_state.page = "library"
    if 'current_document' not in st.session_state:
        st.session_state.current_document = ""
    
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
    
    # Document library management in sidebar (always visible)
    show_document_library(app)
    
    # Logout button in sidebar
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = "professional_user"
        st.session_state.clear()
        st.rerun()
    
    # Page routing
    if st.session_state.page == "library":
        show_library_page()
    elif st.session_state.page == "upload":
        show_upload_page(app)
    elif st.session_state.page == "chat":
        show_chat_page(app)

def show_library_page():
    """Main library page showing welcome and instructions"""
    show_professional_header()
    
    # Welcome section
    st.markdown(f"""
    <div style="background: #134E4A; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border-left: 4px solid #10B981;">
        <h3 style="color: #6EE7B7; margin: 0 0 0.25rem 0; font-size: 1rem;">👋 Welcome back, <strong>{st.session_state.username}</strong>!</h3>
        <p style="color: #A7F3D0; margin: 0; font-size: 0.8rem; line-height: 1.2;">
            Ready to analyze your professional documents with AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start guide
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: #1E293B; padding: 1rem; border-radius: 6px; border: 1px solid #475569; height: 100%;">
            <h4 style="color: #60A5FA; margin: 0 0 0.5rem 0; font-size: 0.9rem;">🚀 Quick Start</h4>
            <div style="color: #94A3B8; line-height: 1.2; font-size: 0.75rem;">
                <p style="margin: 0.25rem 0;">
                    <strong style="color: #E2E8F0;">1.</strong> Click <strong>"📤 Upload New Document"</strong> in sidebar
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong style="color: #E2E8F0;">2.</strong> Upload your PDF or Word document
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong style="color: #E2E8F0;">3.</strong> Start chatting with your document
                </p>
                <p style="margin: 0.25rem 0;">
                    <strong style="color: #E2E8F0;">4.</strong> Access previous documents from sidebar
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #1E293B; padding: 1rem; border-radius: 6px; border: 1px solid #475569; height: 100%;">
            <h4 style="color: #60A5FA; margin: 0 0 0.5rem 0; font-size: 0.9rem;">📄 Supported Documents</h4>
            <div style="color: #94A3B8; line-height: 1.2; font-size: 0.75rem;">
                <p style="margin: 0.25rem 0;">
                    <span style="color: #10B981;">✓</span> HR & Employment policies
                </p>
                <p style="margin: 0.25rem 0;">
                    <span style="color: #10B981;">✓</span> Insurance documents
                </p>
                <p style="margin: 0.25rem 0;">
                    <span style="color: #10B981;">✓</span> Legal & Compliance files
                </p>
                <p style="margin: 0.25rem 0;">
                    <span style="color: #10B981;">✓</span> Financial & Regulatory docs
                </p>
                <p style="margin: 0.25rem 0;">
                    <span style="color: #10B981;">✓</span> Technical & IT policies
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity or stats (if any documents exist)
    if 'app' in st.session_state:
        sessions = st.session_state.app.get_user_sessions()
        if sessions:
            st.markdown("---")
            st.markdown("### 📊 Your Document Activity")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_docs = len(sessions)
            total_chunks = sum(session.get('chunks_count', 0) for session in sessions)
            doc_types = set(session.get('document_type', 'Unknown') for session in sessions)
            recent_doc = sessions[0] if sessions else None
            
            with col1:
                st.metric("📄 Documents", total_docs)
            with col2:
                st.metric("🧩 Total Chunks", total_chunks)
            with col3:
                st.metric("📊 Document Types", len(doc_types))
            with col4:
                if recent_doc:
                    st.metric("🕐 Last Upload", recent_doc.get('document_name', 'Unknown')[:15] + "...")
                else:
                    st.metric("🕐 Last Upload", "None")
        else:
            # First time user experience
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem 0.75rem; background: #1E293B; border-radius: 6px; border: 1px solid #475569; margin: 1rem 0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <h3 style="color: #60A5FA; margin: 0 0 0.5rem 0; font-size: 1rem;">No documents yet</h3>
                <p style="color: #94A3B8; margin: 0 0 1rem 0; font-size: 0.85rem;">
                    Upload your first document to start analyzing with AI
                </p>
                <div style="display: inline-block; background: #3B82F6; color: white; padding: 0.375rem 1rem; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">
                    ← Click "Upload New Document" to begin
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()