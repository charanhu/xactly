# FILE_GUIDE.md

# Complete File Guide and Descriptions

## Project Files Overview

This solution consists of **8 core files** + **3 optional support files** + **3 documentation files**.

---

## Core Application Files (8 files)

### 1. **main.py** - FastAPI Server and API Routes
**Purpose**: HTTP server that handles all API requests
**Size**: ~400 lines
**Key Components**:
- FastAPI application initialization
- Request/Response models (Pydantic)
- 11 API endpoints
- Session management (in-memory dict)
- CORS middleware
- Error handling and logging

**Key Endpoints Defined**:
- `GET /health` - System health
- `POST /api/kb/initialize` - Load PDFs
- `GET /api/kb/info` - KB statistics
- `POST /api/kb/search` - Direct KB search
- `POST /api/chat/create` - New chat
- `POST /api/chat/{chat_id}/message` - Send message
- `GET /api/chat/{chat_id}/history` - Get history
- `GET /api/chat/{chat_id}/clear` - Clear history
- `GET /api/tickets/{ticket_id}` - Ticket info
- `GET /api/tickets` - List tickets
- `GET /api/chats` - Active chats list

**Dependencies**: FastAPI, Uvicorn, Pydantic
**Run**: `python main.py`

---

### 2. **config.py** - Configuration Management
**Purpose**: Centralized configuration and environment setup
**Size**: ~50 lines
**Key Settings**:
- OpenAI API key and model
- ChromaDB path and collection name
- Data folder path
- API host/port
- Agent parameters (temperature, max_tokens)
- Knowledge base parameters (chunk size, overlap, search results)

**Key Functions**:
- Load environment variables via dotenv
- Create necessary directories
- Validate settings on startup

**Dependencies**: python-dotenv, pathlib

---

### 3. **knowledge_base.py** - Vector Database Management
**Purpose**: Handle PDF ingestion and semantic search
**Size**: ~300 lines
**Key Components**:
- ChromaDB client initialization
- OpenAI embeddings initialization
- PDF loading and parsing
- Document chunking
- Embedding generation
- Semantic search with similarity scoring
- Collection management

**Key Functions**:
- `load_pdfs()` - Load all PDFs from data folder
- `chunk_documents()` - Split documents into chunks
- `ingest_documents()` - Generate embeddings and store
- `search()` - Semantic search
- `initialize_knowledge_base()` - Full initialization pipeline
- `get_collection_info()` - KB statistics
- `clear_knowledge_base()` - Reset KB

**Dependencies**: chromadb, langchain, openai, pypdf
**Persistence**: Files stored at `./kb_index/`

---

### 4. **ticket_system.py** - Mock Jira-like System
**Purpose**: Manage customer support tickets
**Size**: ~200 lines
**Key Components**:
- In-memory ticket database (3 sample tickets)
- Ticket CRUD operations
- Search functionality
- Status management

**Sample Tickets**:
- TICKET-001: Alice Johnson - "Cannot access account"
- TICKET-002: Bob Smith - "Product not working"
- TICKET-003: Charlie Brown - "Billing inquiry"

**Key Functions**:
- `get_ticket()` - Retrieve by ID
- `create_ticket()` - Create new ticket
- `update_ticket_status()` - Update status
- `get_customer_tickets()` - Get by customer
- `search_tickets()` - Keyword search
- `get_ticket_summary()` - Formatted summary

**Dependencies**: None (pure Python)
**Easy Integration**: Replace with real Jira API

---

### 5. **support_agent.py** - AI Agent Logic
**Purpose**: Orchestrate conversations and coordinate components
**Size**: ~350 lines
**Key Components**:
- LangChain ChatOpenAI integration
- Knowledge base search coordination
- Ticket context retrieval
- Conversation history management
- LLM prompt building
- Response generation

**Key Functions**:
- `process_message()` - Main message handler
- `_search_knowledge_base()` - Query KB
- `_get_ticket_context()` - Fetch ticket info
- `_format_kb_context()` - Format search results
- `_create_system_prompt()` - Build LLM prompt
- `get_chat_history()` - Retrieve history
- `clear_chat_history()` - Clear history

**Dependencies**: langchain, openai

---

### 6. **requirements.txt** - Python Dependencies
**Purpose**: List all required Python packages
**Size**: 11 lines
**Key Packages**:
- chromadb (vector database)
- langchain (LLM orchestration)
- langchain-community (additional tools)
- langchain-openai (OpenAI integration)
- fastapi (web framework)
- uvicorn (ASGI server)
- pydantic (data validation)
- pypdf (PDF parsing)
- python-dotenv (env file support)

**Install**: `pip install -r requirements.txt`

---

### 7. **.env.example** - Environment Template
**Purpose**: Template for configuration
**Size**: 7 lines
**Variables**:
- OPENAI_API_KEY - Your OpenAI key
- OPENAI_MODEL - Model to use
- CHROMA_DB_PATH - Vector DB location
- DATA_FOLDER - PDF storage location
- API_HOST - Server host
- API_PORT - Server port
- DEBUG - Debug mode

**Setup**: Copy to `.env` and fill in values

---

### 8. **.gitignore** (Recommended)
**Purpose**: Prevent committing sensitive files
**Typical Content**:
```
.env
.env.local
__pycache__/
*.pyc
*.pyo
venv/
kb_index/
.DS_Store
*.log
```

---

## Support Files (3 optional files)

### 1. **test_client.py** - Testing and Debugging
**Purpose**: Test the API without UI
**Size**: ~300 lines
**Key Functions**:
- `test_health_check()` - Verify server
- `test_initialize_kb()` - Load PDFs
- `test_kb_info()` - Get KB stats
- `test_list_tickets()` - View tickets
- `test_create_chat()` - Start conversation
- `test_send_message()` - Send messages
- `test_chat_history()` - View history
- `run_full_test()` - Complete workflow
- `interactive_mode()` - Interactive CLI

**Usage**:
```bash
python test_client.py              # Run full test
python test_client.py interactive  # Interactive mode
python test_client.py search "query"  # Search KB
```

**Dependencies**: requests

---

### 2. **mock_data_generator.py** - Sample Data Creation
**Purpose**: Generate test PDFs
**Size**: ~150 lines
**Creates**:
- `data/faq.pdf` - FAQ document
- `data/troubleshooting.pdf` - Troubleshooting guide
- `data/policies.pdf` - Company policies

**Usage**:
```bash
pip install reportlab
python mock_data_generator.py
```

**Dependencies**: reportlab, pathlib

---

### 3. **Dockerfile** (Recommended for Production)
**Purpose**: Container for deployment
**Sample Content**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

**Build**: `docker build -t support-agent .`
**Run**: `docker run -p 8000:8000 -e OPENAI_API_KEY=sk-xxx support-agent`

---

## Documentation Files (3 comprehensive guides)

### 1. **README.md** - Main Documentation
**Purpose**: Complete project documentation
**Sections**:
- Project structure
- Setup instructions
- API endpoints
- Architecture overview
- Key features
- Troubleshooting
- Performance considerations
- Monitoring & logging
- Future enhancements

**Best For**: Full understanding of the system

---

### 2. **QUICK_START.md** - Quick Setup Guide
**Purpose**: Get started in 5 minutes
**Sections**:
- Prerequisites
- 5-minute setup
- Testing options (Swagger, cURL, Python)
- Common issues & solutions
- Example workflows
- Configuration tweaking
- Production checklist

**Best For**: Rapid deployment and testing

---

### 3. **ASSUMPTIONS_AND_ARCHITECTURE.md** - Technical Details
**Purpose**: Design decisions and technical architecture
**Sections**:
- 10 key assumptions
- Architecture diagrams
- Data flow
- Component descriptions
- Integration points
- Performance considerations
- Security considerations
- Testing strategy
- Deployment options

**Best For**: Understanding design and extending system

---

### 4. **SOLUTION_OVERVIEW.md** - Executive Summary
**Purpose**: High-level overview and solution summary
**Sections**:
- Executive summary
- Problem statement
- Solution architecture
- Setup instructions
- Usage examples
- Data flow
- Component descriptions
- API specification
- Performance metrics
- Testing guide

**Best For**: Understanding what solution does

---

## Directory Structure

```
customer-support-agent/
│
├── Core Application Files
├── main.py                      (FastAPI server + routes)
├── config.py                    (Configuration management)
├── knowledge_base.py            (Vector DB + PDF handling)
├── ticket_system.py             (Mock ticket system)
├── support_agent.py             (AI agent logic)
│
├── Configuration & Dependencies
├── requirements.txt             (Python packages)
├── .env.example                (Environment template)
├── .env                         (ACTUAL environment - create from .env.example)
├── .gitignore                  (Git ignore rules)
│
├── Support & Testing Files
├── test_client.py              (Test suite + CLI)
├── mock_data_generator.py      (Generate sample PDFs)
├── Dockerfile                  (Container image)
│
├── Documentation
├── README.md                   (Full documentation)
├── QUICK_START.md              (Quick setup guide)
├── ASSUMPTIONS_AND_ARCHITECTURE.md  (Technical architecture)
├── SOLUTION_OVERVIEW.md        (Executive summary)
├── FILE_GUIDE.md              (This file)
│
├── Data & Storage (auto-created)
├── data/                       (PDF storage location)
│   ├── faq.pdf                (Sample FAQ)
│   ├── troubleshooting.pdf    (Sample troubleshooting guide)
│   └── policies.pdf           (Sample policies)
│
├── kb_index/                   (ChromaDB vector store)
│   ├── 98ef123a.parquet       (Data files)
│   └── metadata.json
│
└── venv/                       (Virtual environment)
    ├── bin/
    ├── lib/
    └── pyvenv.cfg
```

---

## File Dependencies

### Import Map
```
main.py
├─ knowledge_base.py
├─ ticket_system.py
├─ support_agent.py
│  ├─ knowledge_base.py
│  └─ ticket_system.py
└─ config.py

config.py
└─ (no internal dependencies)

support_agent.py
├─ knowledge_base.py
├─ ticket_system.py
└─ config.py

knowledge_base.py
└─ config.py

ticket_system.py
└─ (no internal dependencies)

test_client.py
└─ (external requests library)

mock_data_generator.py
└─ (external reportlab library)
```

---

## File Relationships

### Data Flow Through Files

1. **User Request** → `main.py` (API handler)
2. **Chat Session** → `main.py` (session storage)
3. **Process Message** → `support_agent.py` (orchestrator)
4. **Search KB** → `knowledge_base.py` (ChromaDB)
5. **Get Ticket** → `ticket_system.py` (Jira mock)
6. **Build Prompt** → `support_agent.py` (context assembly)
7. **Call LLM** → OpenAI API (via support_agent.py)
8. **Return Response** → `main.py` (response formatting)
9. **Send to Client** → HTTP response

---

## Configuration Usage

**config.py** is imported by:
- `knowledge_base.py` (for ChromaDB path, chunk size)
- `support_agent.py` (for temperature, max tokens)
- `main.py` (for API port/host)

Changes to `config.py` affect all components automatically.

---

## Updating Files

### To Add Custom Prompt
**File**: `support_agent.py`
**Method**: `_create_system_prompt()`
**Line**: ~50

### To Change LLM Model
**File**: `config.py`
**Variable**: `OPENAI_MODEL`
**Line**: ~15

### To Integrate Real Jira
**File**: `ticket_system.py` (replace entirely)
**Or**: Create `jira_integration.py` and update imports in `main.py`

### To Use Different KB
**File**: `knowledge_base.py`
**Class**: `KnowledgeBase`
**Line**: ~30

---

## File Sizes (Approximate)

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| main.py | 400 | 18KB | API server |
| support_agent.py | 350 | 15KB | Agent logic |
| knowledge_base.py | 300 | 12KB | Vector DB |
| ticket_system.py | 200 | 8KB | Tickets |
| config.py | 50 | 2KB | Config |
| test_client.py | 300 | 12KB | Testing |
| mock_data_generator.py | 150 | 6KB | Sample data |
| **Total Code** | **1,750** | **73KB** | **Python source** |

---

## Installation Checklist

Before running, ensure you have:

- [ ] Python 3.9+ installed
- [ ] pip installed
- [ ] OpenAI API key obtained
- [ ] requirements.txt installed (`pip install -r requirements.txt`)
- [ ] .env file created with OPENAI_API_KEY
- [ ] data/ folder created (optional, for PDFs)
- [ ] All 5 core files in project root (main.py, etc.)

---

## Verification Checklist

After setup, verify:

- [ ] Server starts: `python main.py`
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Swagger UI loads: http://localhost:8000/docs
- [ ] Test suite runs: `python test_client.py`
- [ ] PDFs generated: `python mock_data_generator.py`
- [ ] KB initializes: `POST /api/kb/initialize`
- [ ] Chat created: `POST /api/chat/create`
- [ ] Message processed: `POST /api/chat/{id}/message`

---

## Next Steps

1. **Understand Structure**: Read this file
2. **Review Code**: Start with main.py
3. **Read Docs**: Review README.md
4. **Set Up**: Follow QUICK_START.md
5. **Test**: Run test_client.py
6. **Customize**: Edit support_agent.py system prompt
7. **Extend**: Add real Jira integration
8. **Deploy**: Use Dockerfile for production

---

## File Usage by Role

### For Users/Testers
- README.md (understand what it does)
- QUICK_START.md (how to set up)
- test_client.py (how to test)
- .env.example (configuration)

### For Developers
- main.py (API structure)
- support_agent.py (core logic)
- config.py (settings)
- ASSUMPTIONS_AND_ARCHITECTURE.md (design)

### For DevOps/Deployment
- requirements.txt (dependencies)
- Dockerfile (containerization)
- config.py (configuration)
- QUICK_START.md (deployment steps)

### For Integration
- ticket_system.py (replace with Jira)
- knowledge_base.py (swap vector DB)
- support_agent.py (customize prompt)
- config.py (adjust parameters)

---

This complete file guide should help you understand the project structure and know exactly where to look for specific functionality!
