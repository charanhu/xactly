# ASSUMPTIONS_AND_ARCHITECTURE.md

## Assumptions Made

### 1. **Knowledge Base Format**
- PDFs are stored in a local `data/` folder
- PDFs contain unstructured text data (company policies, troubleshooting guides, FAQs)
- PDFs are readable and searchable (not scanned images)
- Documents are in English (can be extended for multilingual support)

### 2. **System of Record (Tickets)**
- Using mock Jira-like system for demonstration
- Easily replaceable with real Jira API integration (requires JIRA_API_TOKEN)
- Each ticket has: ID, status, priority, customer name, description, category
- Ticket IDs follow pattern: TICKET-XXX

### 3. **LLM Provider**
- Using OpenAI API (GPT-3.5-turbo or GPT-4)
- Requires valid OPENAI_API_KEY in environment
- Alternative providers (Anthropic, Cohere, local models) can be integrated via LangChain

### 4. **Vector Database**
- Using ChromaDB for vector embeddings and semantic search
- Runs locally (can be configured for server mode)
- Embeddings generated using OpenAI's text-embedding-3-small model
- Persistent storage on disk at `./kb_index`

### 5. **Session Management**
- Chat sessions stored in-memory during runtime
- No authentication/authorization implemented
- Session timeout: 30 minutes (configurable)
- For production: migrate to Redis or PostgreSQL

### 6. **API Architecture**
- RESTful API using FastAPI
- No API key authentication (add for production)
- CORS enabled for all origins (restrict in production)
- Single-server deployment (scale with distributed queue/load balancer)

### 7. **Conversation Context**
- Each chat maintains conversation history (up to 50 messages)
- Context window: Full chat history passed to LLM
- No message summarization (implement for long conversations)

### 8. **Knowledge Retrieval**
- Top 5 most relevant documents returned per query
- Similarity score calculated using cosine distance
- No result filtering based on confidence threshold

### 9. **Logging & Monitoring**
- Basic console logging implemented
- No persistent log storage (add for production)
- No metrics collection (add Prometheus for production)

### 10. **Error Handling**
- Graceful fallbacks for LLM/KB errors
- Generic error messages to users
- Detailed logging for debugging

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ /api/chat    │  │ /api/kb      │  │ /api/tickets │     │
│  │  - create    │  │  - init      │  │  - get       │     │
│  │  - message   │  │  - search    │  │  - list      │     │
│  │  - history   │  │  - info      │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                  ↓                  ↓              │
└─────────────────────────────────────────────────────────────┘
         ↓                  ↓                  ↓
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Support  │  │ Knowledge  │  │   Ticket   │
    │   Agent    │  │    Base    │  │   System   │
    └────────────┘  └────────────┘  └────────────┘
         ↓                  ↓                  ↓
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ LangChain  │  │  ChromaDB  │  │    Mock    │
    │ OpenAI     │  │  Embeddings│  │    Jira    │
    │ ChatGPT    │  │  Vector DB │  │   System   │
    └────────────┘  └────────────┘  └────────────┘
         ↓                  ↓                  ↓
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  OpenAI    │  │   Local    │  │   In-Mem   │
    │    API     │  │   Files    │  │  Storage   │
    └────────────┘  └────────────┘  └────────────┘
```

---

## Data Flow

### Chat Initialization Flow
```
1. Client creates chat → POST /api/chat/create
2. FastAPI generates unique chat_id (UUID)
3. Session stored in chat_sessions dict
4. Return chat_id to client
```

### Message Processing Flow
```
1. Client sends message → POST /api/chat/{chat_id}/message
2. FastAPI validates chat_id exists
3. Support Agent receives message
   a. Extract ticket context (if ticket_id provided)
   b. Search knowledge base (semantic search via ChromaDB)
   c. Retrieve top 5 similar documents with similarity scores
   d. Build LLM prompt with system message + KB context + conversation history
4. LLM (ChatGPT) generates response
5. Response + KB sources + ticket info returned to client
6. Message pair stored in chat history
```

### Knowledge Base Initialization Flow
```
1. Admin calls → POST /api/kb/initialize
2. System loads all PDFs from data/ folder
3. PDFs split into chunks (1000 chars, 200 overlap)
4. Generate embeddings for each chunk (OpenAI API)
5. Store in ChromaDB with metadata (source, page, chunk)
6. Persist to disk at kb_index/
```

### Knowledge Base Search Flow
```
1. User query received by Support Agent
2. Generate embedding for query (OpenAI API)
3. Query ChromaDB for nearest neighbors
4. Return top 5 documents with similarity scores
5. Format results with source and page info
6. Include in LLM context
```

---

## Component Descriptions

### 1. **main.py** - FastAPI Server
- **Purpose**: HTTP API server and routing
- **Key Functions**:
  - Health check endpoint
  - Chat management (create, message, history)
  - Knowledge base management
  - Ticket information retrieval
- **Dependencies**: FastAPI, Uvicorn, Pydantic

### 2. **support_agent.py** - AI Agent Logic
- **Purpose**: Orchestrates knowledge base and ticket access
- **Key Functions**:
  - Process user messages
  - Search knowledge base
  - Build LLM prompts with context
  - Maintain conversation history
  - Generate responses via ChatGPT
- **Dependencies**: LangChain, OpenAI, Knowledge Base, Ticket System

### 3. **knowledge_base.py** - Vector Database
- **Purpose**: Manages PDF ingestion and semantic search
- **Key Functions**:
  - Load PDFs from disk
  - Split documents into chunks
  - Generate embeddings (OpenAI)
  - Store in ChromaDB
  - Semantic search with cosine similarity
- **Dependencies**: ChromaDB, LangChain, OpenAI, PyPDF

### 4. **ticket_system.py** - Ticket Management
- **Purpose**: Mock Jira-like system for ticket access
- **Key Functions**:
  - Get ticket by ID
  - Create new tickets
  - Update ticket status
  - Search tickets
  - Get customer tickets
- **Dependencies**: None (standalone Python)

### 5. **config.py** - Configuration Management
- **Purpose**: Centralized configuration
- **Settings**:
  - API host/port
  - OpenAI API key and model
  - ChromaDB path
  - Data folder path
  - Agent parameters (temperature, max_tokens)
  - Knowledge base parameters (chunk size, search results)

---

## Integration Points

### With Jira
**Current**: Mock system in `ticket_system.py`

**To integrate real Jira**:
```python
from jira import JIRA

class JiraTicketSystem:
    def __init__(self, jira_url, api_token):
        self.jira = JIRA(server=jira_url, token_auth=api_token)
    
    def get_ticket(self, ticket_id):
        issue = self.jira.issue(ticket_id)
        return {
            "ticket_id": issue.key,
            "title": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            # ... more fields
        }
```

### With Different LLMs
**Current**: OpenAI (ChatGPT)

**To use other LLMs via LangChain**:
```python
# Anthropic Claude
from langchain.chat_models import ChatAnthropic
llm = ChatAnthropic(api_key=ANTHROPIC_KEY)

# Local models (Ollama)
from langchain.llms import Ollama
llm = Ollama(model="mistral")

# Google's PaLM
from langchain.chat_models import ChatGooglePalm
llm = ChatGooglePalm(google_api_key=PALM_KEY)
```

### With Different Vector DBs
**Current**: ChromaDB

**To use other vector databases**:
```python
# Pinecone
from langchain.vectorstores import Pinecone
db = Pinecone.from_documents(docs, embeddings, index_name="support")

# Weaviate
from langchain.vectorstores import Weaviate
db = Weaviate.from_documents(docs, embeddings, client=client)

# Milvus
from langchain.vectorstores import Milvus
db = Milvus.from_documents(docs, embeddings)
```

### With Session Storage
**Current**: In-memory dictionary

**To use persistent storage**:
```python
# Redis
import redis
redis_client = redis.Redis(host='localhost')

# PostgreSQL
import psycopg2
conn = psycopg2.connect("dbname=support user=postgres")

# MongoDB
from pymongo import MongoClient
mongo_client = MongoClient("mongodb://localhost")
```

---

## Performance Considerations

### Query Latency
- **KB Embedding Generation**: ~100ms (OpenAI API)
- **KB Search**: ~10-50ms (ChromaDB)
- **LLM Response**: 2-5 seconds (network dependent)
- **Total**: 2-6 seconds per message

### Optimization Strategies
1. **Embedding Caching**: Cache common queries
2. **Batch Processing**: Process multiple messages in parallel
3. **KB Indexing**: Pre-compute frequent queries
4. **Response Streaming**: Stream LLM output to client
5. **Connection Pooling**: Reuse HTTP connections

### Scaling Approaches
1. **Horizontal**: Load balancer + multiple API instances
2. **Caching**: Redis for session/embedding cache
3. **Async**: Use FastAPI async endpoints
4. **Batch**: Queue for offline processing
5. **Distributed DB**: PostgreSQL for session persistence

---

## Security Considerations

### Current Gaps (Add for Production)
- [ ] API authentication (API keys, JWT)
- [ ] Rate limiting (prevent abuse)
- [ ] CORS restrictions (specific origins)
- [ ] HTTPS/TLS (encrypted communication)
- [ ] Input validation (prevent injection)
- [ ] Output sanitization (prevent XSS if web UI)
- [ ] PII handling (redact personal information)
- [ ] Data encryption (at rest and in transit)
- [ ] Access logging (audit trail)
- [ ] Secret management (env vars + vault)

---

## Testing Strategy

### Unit Tests
```python
# test_knowledge_base.py
def test_pdf_loading():
    kb = KnowledgeBase()
    docs = kb.load_pdfs()
    assert len(docs) > 0

def test_semantic_search():
    kb = KnowledgeBase()
    results = kb.search("login issue")
    assert len(results) > 0
    assert results[0][2] > 0.5  # Similarity score
```

### Integration Tests
```python
# test_api.py
def test_full_conversation():
    # Create chat → Send message → Verify response
    chat_id = create_chat("John", "TICKET-001")
    response = send_message(chat_id, "Can't log in")
    assert response["agent_response"]
    assert len(response["kb_sources"]) > 0
```

### Load Tests
```bash
# Using locust
locust -f locustfile.py --users 100 --spawn-rate 10
```

---

## Deployment Options

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./kb_index:/app/kb_index
```

### Cloud Deployment
- **AWS**: ECS/Fargate + RDS + S3
- **GCP**: Cloud Run + Cloud SQL + Cloud Storage
- **Azure**: App Service + SQL Database + Blob Storage
- **Heroku**: Simple push deployment (git push heroku main)

---

## Future Enhancements

### Phase 2
- [ ] Real Jira integration
- [ ] PostgreSQL for persistence
- [ ] Redis for caching
- [ ] WebSocket for real-time updates
- [ ] Admin dashboard

### Phase 3
- [ ] Sentiment analysis
- [ ] Conversation summarization
- [ ] Multi-language support
- [ ] Custom fine-tuned models
- [ ] Analytics/metrics dashboard

### Phase 4
- [ ] Multi-agent collaboration
- [ ] Hierarchical ticket routing
- [ ] Auto-escalation rules
- [ ] Customer satisfaction surveys
- [ ] Revenue impact analysis
