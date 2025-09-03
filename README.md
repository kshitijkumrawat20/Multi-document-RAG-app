# ClariDoc Professional RAG Platform

ClariDoc is a professional document analysis platform designed for enterprise domains including HR/Employment, Insurance, Legal/Compliance, Financial/Regulatory, Government/Public Policy, and Technical/IT Policies.

## Frontend Developer Guide

This guide provides comprehensive specifications for recreating the ClariDoc frontend interface in any tech stack while maintaining professional standards and seamless API integration.

### Design Specifications

#### Theme & Visual Identity
- **Primary Theme**: Dark/Professional theme for reduced eye strain and professional appearance
- **Color Palette**:
  - Background: `#0E1117` (main), `#1E2329` (secondary)
  - Text: `#FAFAFA` (primary), `#C7C7C7` (secondary)
  - Accent: `#FF6B6B` (primary actions), `#4ECDC4` (success states)
  - Borders: `#2E3440` for subtle separations
- **Typography**: 
  - Headers: Clean sans-serif, bold weights
  - Body: Readable sans-serif, 14-16px base size
  - Code/Technical: Monospace font family

#### Layout Structure
```
┌─────────────────────────────────┐
│           Header               │
│  ClariDoc + Professional Tag    │
├─────────────────────────────────┤
│         File Upload            │
│    (Drag & Drop + Browse)      │
├─────────────────────────────────┤
│      Document Analysis         │
│   (Domain Selection + Query)   │
├─────────────────────────────────┤
│         Results Panel          │
│  ┌─────────┬─────────────────┐  │
│  │Metadata │   AI Response   │  │
│  │ Panel   │     Section     │  │
│  └─────────┴─────────────────┘  │
├─────────────────────────────────┤
│      Document Sources          │
│   (Top 3 relevant chunks)      │
└─────────────────────────────────┘
```

### Component Specifications

#### 1. Professional Header Component
```javascript
// Header Component Specification
const ProfessionalHeader = {
  layout: "horizontal-flex",
  elements: [
    {
      type: "logo",
      text: "ClariDoc",
      style: {
        fontSize: "2.5rem",
        fontWeight: "bold",
        color: "#FAFAFA",
        background: "linear-gradient(135deg, #FF6B6B, #4ECDC4)",
        backgroundClip: "text",
        textFillColor: "transparent"
      }
    },
    {
      type: "tagline",
      text: "Professional Document Analysis Platform",
      style: {
        fontSize: "1.1rem",
        color: "#C7C7C7",
        fontStyle: "italic",
        marginLeft: "1rem"
      }
    }
  ],
  containerStyle: {
    padding: "2rem 0",
    borderBottom: "2px solid #2E3440",
    marginBottom: "2rem"
  }
}
```

#### 2. File Upload Component
```javascript
const FileUploadComponent = {
  type: "drag-drop-zone",
  acceptedTypes: [".pdf", ".docx", ".txt"],
  maxSize: "10MB",
  style: {
    border: "2px dashed #4ECDC4",
    borderRadius: "12px",
    padding: "3rem",
    backgroundColor: "#1E2329",
    textAlign: "center",
    transition: "all 0.3s ease"
  },
  hoverStyle: {
    borderColor: "#FF6B6B",
    backgroundColor: "#2A2D35"
  },
  elements: [
    {
      type: "icon",
      name: "upload-cloud",
      size: "3rem",
      color: "#4ECDC4"
    },
    {
      type: "text-primary",
      content: "Drop your document here or click to browse",
      style: { fontSize: "1.2rem", color: "#FAFAFA" }
    },
    {
      type: "text-secondary",
      content: "Supports PDF, DOCX, TXT files up to 10MB",
      style: { fontSize: "0.9rem", color: "#C7C7C7" }
    }
  ]
}
```

#### 3. Domain Selection Component
```javascript
const DomainSelector = {
  type: "radio-button-group",
  options: [
    { value: "hr_employment", label: "HR/Employment", icon: "users" },
    { value: "insurance", label: "Insurance", icon: "shield" },
    { value: "legal_compliance", label: "Legal/Compliance", icon: "scale" },
    { value: "financial_regulatory", label: "Financial/Regulatory", icon: "dollar-sign" },
    { value: "government_policy", label: "Government/Public Policy", icon: "building" },
    { value: "technical_it", label: "Technical/IT Policies", icon: "cpu" }
  ],
  style: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "1rem",
    margin: "1.5rem 0"
  },
  buttonStyle: {
    padding: "1rem",
    border: "1px solid #2E3440",
    borderRadius: "8px",
    backgroundColor: "#1E2329",
    color: "#FAFAFA",
    cursor: "pointer",
    transition: "all 0.3s ease"
  },
  activeStyle: {
    borderColor: "#4ECDC4",
    backgroundColor: "#2A3B3C"
  }
}
```

#### 4. Query Input Component
```javascript
const QueryInput = {
  type: "textarea",
  placeholder: "Ask questions about your document (e.g., 'What are the key policies?', 'Summarize the main points')",
  style: {
    width: "100%",
    minHeight: "120px",
    padding: "1rem",
    backgroundColor: "#1E2329",
    border: "1px solid #2E3440",
    borderRadius: "8px",
    color: "#FAFAFA",
    fontSize: "1rem",
    fontFamily: "inherit",
    resize: "vertical"
  },
  focusStyle: {
    borderColor: "#4ECDC4",
    outline: "none",
    boxShadow: "0 0 0 2px rgba(78, 205, 196, 0.2)"
  }
}
```

#### 5. Metadata Display Panel
```javascript
const MetadataPanel = {
  layout: "card",
  style: {
    backgroundColor: "#1E2329",
    border: "1px solid #2E3440",
    borderRadius: "12px",
    padding: "1.5rem",
    marginBottom: "1.5rem"
  },
  header: {
    text: "Document Metadata",
    style: {
      fontSize: "1.3rem",
      fontWeight: "bold",
      color: "#4ECDC4",
      marginBottom: "1rem"
    }
  },
  fields: [
    { label: "Document Type", key: "document_type" },
    { label: "Domain", key: "domain" },
    { label: "Key Topics", key: "key_topics", type: "array" },
    { label: "Confidence Score", key: "confidence", type: "percentage" },
    { label: "Processing Time", key: "processing_time" },
    { label: "Page Count", key: "page_count" }
  ],
  fieldStyle: {
    display: "flex",
    justifyContent: "space-between",
    padding: "0.5rem 0",
    borderBottom: "1px solid #2E3440"
  }
}
```

#### 6. AI Response Section
```javascript
const AIResponseSection = {
  layout: "card",
  style: {
    backgroundColor: "#1E2329",
    border: "1px solid #2E3440",
    borderRadius: "12px",
    padding: "1.5rem",
    minHeight: "300px"
  },
  header: {
    text: "AI Analysis",
    style: {
      fontSize: "1.3rem",
      fontWeight: "bold",
      color: "#FF6B6B",
      marginBottom: "1rem"
    }
  },
  contentStyle: {
    lineHeight: "1.6",
    color: "#FAFAFA",
    fontSize: "1rem"
  },
  loadingState: {
    type: "spinner",
    text: "Analyzing document...",
    style: {
      textAlign: "center",
      padding: "2rem",
      color: "#C7C7C7"
    }
  }
}
```

#### 7. Document Sources Component
```javascript
const DocumentSources = {
  layout: "expansion-panel",
  title: "📄 Top Document Sources",
  style: {
    backgroundColor: "#1E2329",
    border: "1px solid #2E3440",
    borderRadius: "12px",
    marginTop: "1.5rem"
  },
  headerStyle: {
    padding: "1rem",
    fontSize: "1.2rem",
    fontWeight: "bold",
    color: "#4ECDC4",
    cursor: "pointer"
  },
  sourceCardStyle: {
    backgroundColor: "#0E1117",
    border: "1px solid #2E3440",
    borderRadius: "8px",
    padding: "1rem",
    margin: "0.5rem 0"
  },
  sourceFields: [
    { label: "Page", key: "page_number" },
    { label: "Relevance", key: "relevance_score", type: "percentage" },
    { label: "Content", key: "content", type: "text-preview", maxLength: 200 }
  ]
}
```

### API Integration Specifications

#### Environment Configuration
```javascript
// Environment Variables
const CONFIG = {
  API_BASE_URL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  WEBSOCKET_URL: process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws",
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_FORMATS: [".pdf", ".docx", ".txt"]
}
```

#### API Endpoints & Methods

##### 1. Session Management
```javascript
// Create new session
POST ${API_BASE_URL}/api/v1/create_session
Body: { user_id: string }
Response: { session_id: string, status: string }

// Get session
GET ${API_BASE_URL}/api/v1/session/{session_id}
Response: { session_id: string, user_id: string, created_at: string }
```

##### 2. Document Upload & Processing
```javascript
// Upload document
POST ${API_BASE_URL}/api/v1/upload_document
Headers: { "Content-Type": "multipart/form-data" }
Body: FormData {
  file: File,
  session_id: string,
  domain: string // One of the domain values
}
Response: {
  success: boolean,
  filename: string,
  file_size: number,
  message: string
}

// Process document for analysis
POST ${API_BASE_URL}/api/v1/process_document
Body: {
  session_id: string,
  filename: string,
  domain: string
}
Response: {
  success: boolean,
  processing_id: string,
  metadata: {
    document_type: string,
    domain: string,
    key_topics: string[],
    confidence: number,
    processing_time: string,
    page_count: number
  }
}
```

##### 3. Query Processing
```javascript
// Submit query
POST ${API_BASE_URL}/api/v1/query
Body: {
  session_id: string,
  query: string,
  domain: string,
  filename?: string
}
Response: {
  response: string,
  sources: Array<{
    content: string,
    page_number: number,
    relevance_score: number,
    metadata: object
  }>,
  processing_time: number
}
```

##### 4. Health Check
```javascript
// Health check
GET ${API_BASE_URL}/health
Response: { status: "healthy", timestamp: string }
```

### State Management Specifications

#### Application State Structure
```javascript
const AppState = {
  // Session Management
  session: {
    sessionId: null,
    userId: null,
    isActive: false
  },
  
  // File Management
  file: {
    uploaded: null,
    uploading: false,
    processed: false,
    processing: false,
    metadata: null
  },
  
  // Domain & Query
  domain: {
    selected: null,
    options: [/* domain options */]
  },
  
  query: {
    text: "",
    response: null,
    loading: false,
    sources: []
  },
  
  // UI State
  ui: {
    showSources: false,
    darkMode: true,
    sidebarOpen: false
  },
  
  // Error Handling
  errors: {
    upload: null,
    processing: null,
    query: null
  }
}
```

#### Key Action Handlers
```javascript
const ActionHandlers = {
  // File Upload
  handleFileUpload: async (file, domain) => {
    try {
      setState(prev => ({ ...prev, file: { ...prev.file, uploading: true } }));
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', state.session.sessionId);
      formData.append('domain', domain);
      
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/upload_document`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        setState(prev => ({
          ...prev,
          file: {
            ...prev.file,
            uploaded: result.filename,
            uploading: false
          }
        }));
        
        // Trigger document processing
        await handleDocumentProcessing(result.filename, domain);
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        file: { ...prev.file, uploading: false },
        errors: { ...prev.errors, upload: error.message }
      }));
    }
  },
  
  // Document Processing
  handleDocumentProcessing: async (filename, domain) => {
    try {
      setState(prev => ({ ...prev, file: { ...prev.file, processing: true } }));
      
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/process_document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.session.sessionId,
          filename: filename,
          domain: domain
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setState(prev => ({
          ...prev,
          file: {
            ...prev.file,
            processed: true,
            processing: false,
            metadata: result.metadata
          }
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        file: { ...prev.file, processing: false },
        errors: { ...prev.errors, processing: error.message }
      }));
    }
  },
  
  // Query Submission
  handleQuerySubmit: async (queryText) => {
    try {
      setState(prev => ({ ...prev, query: { ...prev.query, loading: true } }));
      
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.session.sessionId,
          query: queryText,
          domain: state.domain.selected,
          filename: state.file.uploaded
        })
      });
      
      const result = await response.json();
      
      setState(prev => ({
        ...prev,
        query: {
          ...prev.query,
          loading: false,
          response: result.response,
          sources: result.sources || []
        }
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        query: { ...prev.query, loading: false },
        errors: { ...prev.errors, query: error.message }
      }));
    }
  }
}
```

### Error Handling & Validation

#### Input Validation
```javascript
const ValidationRules = {
  file: {
    size: (file) => file.size <= CONFIG.MAX_FILE_SIZE,
    type: (file) => CONFIG.SUPPORTED_FORMATS.some(format => 
      file.name.toLowerCase().endsWith(format)
    )
  },
  
  domain: {
    required: (domain) => domain && domain.trim().length > 0,
    valid: (domain) => [
      'hr_employment', 'insurance', 'legal_compliance',
      'financial_regulatory', 'government_policy', 'technical_it'
    ].includes(domain)
  },
  
  query: {
    minLength: (query) => query.trim().length >= 10,
    maxLength: (query) => query.length <= 1000
  }
}
```

#### Error Display Components
```javascript
const ErrorDisplay = {
  type: "alert",
  variants: {
    error: {
      backgroundColor: "#FF6B6B20",
      borderColor: "#FF6B6B",
      color: "#FF6B6B"
    },
    warning: {
      backgroundColor: "#FFA50020",
      borderColor: "#FFA500",
      color: "#FFA500"
    },
    info: {
      backgroundColor: "#4ECDC420",
      borderColor: "#4ECDC4",
      color: "#4ECDC4"
    }
  },
  style: {
    padding: "1rem",
    borderRadius: "8px",
    border: "1px solid",
    margin: "1rem 0"
  }
}
```

### Responsive Design Guidelines

#### Breakpoints
```css
/* Mobile First Approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

#### Mobile Adaptations
- Stack metadata panel above AI response on mobile
- Convert domain selection to dropdown on small screens
- Collapse document sources by default on mobile
- Implement touch-friendly upload area
- Ensure minimum touch target size of 44px

### Performance Considerations

#### Optimization Strategies
1. **Lazy Loading**: Load components only when needed
2. **Debounced Queries**: Prevent excessive API calls during typing
3. **Caching**: Cache processed documents and metadata
4. **Progressive Loading**: Show content as it becomes available
5. **Error Boundaries**: Prevent component crashes from breaking the entire app

#### Loading States
```javascript
const LoadingStates = {
  fileUpload: "Uploading document...",
  processing: "Analyzing document structure...",
  metadata: "Extracting metadata...",
  query: "Generating AI response...",
  sources: "Finding relevant sections..."
}
```

### Accessibility Requirements

#### WCAG Compliance
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- Keyboard navigation support for all interactive elements
- Screen reader compatibility with proper ARIA labels
- Focus indicators with 2px outline in accent color
- Alternative text for all images and icons

#### ARIA Labels
```javascript
const ARIALabels = {
  fileUpload: "aria-label='Upload document for analysis'",
  domainSelect: "aria-label='Select document domain'",
  queryInput: "aria-label='Enter question about document'",
  submitButton: "aria-label='Submit query for AI analysis'",
  metadataPanel: "aria-label='Document metadata information'",
  sourcesPanel: "aria-label='Relevant document sources'"
}
```

### Deployment Configuration

#### Environment Setup
```bash
# Development
NODE_ENV=development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Production
NODE_ENV=production
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_WS_URL=wss://your-api-domain.com/ws
```

#### Build Configuration
```json
{
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.0.0",
    "react-dropzone": "^14.0.0",
    "lucide-react": "^0.263.1"
  }
}
```

### Testing Guidelines

#### Component Testing
```javascript
// Example test structure
describe('FileUpload Component', () => {
  test('accepts valid file types', () => {
    // Test PDF upload
    // Test DOCX upload
    // Test file size validation
  });
  
  test('rejects invalid files', () => {
    // Test unsupported format rejection
    // Test oversized file rejection
  });
});

describe('API Integration', () => {
  test('handles successful document upload', () => {
    // Mock successful API response
    // Verify state updates
  });
  
  test('handles API errors gracefully', () => {
    // Mock API error responses
    // Verify error display
  });
});
```

### Security Considerations

#### Client-Side Security
1. **Input Sanitization**: Sanitize all user inputs before API calls
2. **File Validation**: Strict file type and size checking
3. **CORS Configuration**: Proper cross-origin request handling
4. **API Key Management**: Secure storage of any API keys
5. **Session Management**: Secure session token handling

#### Data Protection
```javascript
const SecurityMeasures = {
  sanitizeInput: (input) => {
    return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  },
  
  validateFileType: (file) => {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    return allowedTypes.includes(file.type);
  },
  
  secureApiCall: async (url, options) => {
    const defaultOptions = {
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    };
    
    return fetch(url, { ...defaultOptions, ...options });
  }
}
```

## Implementation Checklist

### Phase 1: Core Setup
- [ ] Set up project structure with chosen framework
- [ ] Implement dark theme and professional styling
- [ ] Create basic layout with header and main sections
- [ ] Set up state management (Redux/Zustand/Context)
- [ ] Configure API client with environment variables

### Phase 2: File Management
- [ ] Implement file upload component with drag-and-drop
- [ ] Add file validation (type, size, format)
- [ ] Create upload progress indicators
- [ ] Handle upload errors and retry logic
- [ ] Display uploaded file information

### Phase 3: Domain & Analysis
- [ ] Create domain selection component
- [ ] Implement query input with validation
- [ ] Add loading states for all async operations
- [ ] Create metadata display panel
- [ ] Build AI response section with formatting

### Phase 4: Advanced Features
- [ ] Implement document sources panel
- [ ] Add session management
- [ ] Create error handling system
- [ ] Implement responsive design
- [ ] Add accessibility features

### Phase 5: Testing & Deployment
- [ ] Write unit tests for components
- [ ] Create integration tests for API calls
- [ ] Test responsive design across devices
- [ ] Validate accessibility compliance
- [ ] Set up CI/CD pipeline
- [ ] Deploy to production environment

## Support & Maintenance

### Common Issues & Solutions
1. **CORS Errors**: Ensure backend allows frontend domain
2. **File Upload Failures**: Check file size limits and format support
3. **API Timeouts**: Implement retry logic and user feedback
4. **Session Expiry**: Handle session renewal gracefully
5. **Memory Issues**: Implement file cleanup after processing

### Monitoring & Analytics
- Track file upload success rates
- Monitor API response times
- Log error frequencies and types
- Measure user engagement with different domains
- Track query completion rates

