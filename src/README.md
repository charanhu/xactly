# Customer Support Agent - Complete Solution

## Project Structure
```
customer-support-agent/
├── data/                          # PDF knowledge base folder
│   ├── company-policies.pdf
│   ├── troubleshooting-guide.pdf
│   └── faq.pdf
├── kb_index/                      # ChromaDB vector store (auto-created)
├── main.py                        # FastAPI application
├── knowledge_base.py              # Knowledge base management
├── ticket_system.py               # Mock ticket system
├── support_agent.py               # AI agent logic
├── config.py                      # Configuration
├── requirements.txt               # Dependencies
├── .env                          # Environment variables
└── README.md                     # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./kb_index
DATA_FOLDER=./data
```

### 3. Add PDF Knowledge Base
Place your PDF files in the `data/` folder. PDFs will be automatically ingested when the app starts.

### 4. Run the Application
```bash
python main.py
```

The API will be available at: http://localhost:8000

### 5. Interactive API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. Initialize Knowledge Base
```
POST /api/kb/initialize
```
Loads and processes PDF files into the vector database.

### 2. Create Support Chat
```
POST /api/chat/create
Body: {
  "customer_name": "John Doe",
  "ticket_id": "TICKET-123"  # Optional
}
Response: {
  "chat_id": "unique_chat_id",
  "message": "Welcome! How can I help?"
}
```

### 3. Send Message to Agent
```
POST /api/chat/{chat_id}/message
Body: {
  "user_message": "My product won't turn on"
}
Response: {
  "chat_id": "chat_id",
  "agent_response": "I understand...",
  "ticket_info": { ... },  # If ticket_id was provided
  "kb_sources": [...]      # Knowledge base documents used
}
```

### 4. Get Chat History
```
GET /api/chat/{chat_id}/history
Response: [
  {
    "role": "user",
    "message": "My product won't turn on",
    "timestamp": "2024-11-30T18:30:00Z"
  },
  ...
]
```

### 5. Get Ticket Information
```
GET /api/tickets/{ticket_id}
Response: {
  "ticket_id": "TICKET-123",
  "status": "open",
  "priority": "high",
  "description": "..."
}
```

## Architecture

### Components

1. **Knowledge Base (ChromaDB)**
   - Stores embeddings of PDF documents
   - Enables semantic search for relevant information
   - Automatic persistence to disk

2. **Ticket System (Mock)**
   - Simulates Jira-like ticket retrieval
   - Stores ticket metadata and history
   - Used to enrich support conversations

3. **Support Agent (LangChain)**
   - Uses OpenAI's GPT-4 (or GPT-3.5-turbo)
   - Has access to knowledge base retrieval
   - Has access to ticket information
   - Maintains conversation context

4. **API Server (FastAPI)**
   - RESTful endpoints for chat management
   - Real-time response streaming
   - Session management with chat history

## Key Features

✅ **Knowledge Base Integration**: Semantic search using ChromaDB
✅ **Ticket Information Retrieval**: Access to system of record (mock Jira)
✅ **Multi-turn Conversations**: Maintains context across exchanges
✅ **Citation Tracking**: Shows which documents were referenced
✅ **Error Handling**: Graceful fallbacks and error messages
✅ **Production Ready**: Type hints, logging, validation

## Example Usage

### Python Client
```python
import requests

BASE_URL = "http://localhost:8000"

# Create chat
chat_response = requests.post(
    f"{BASE_URL}/api/chat/create",
    json={"customer_name": "Alice", "ticket_id": "TICKET-001"}
)
chat_id = chat_response.json()["chat_id"]

# Send message
msg_response = requests.post(
    f"{BASE_URL}/api/chat/{chat_id}/message",
    json={"user_message": "I can't log in to my account"}
)
print(msg_response.json())
```

### cURL
```bash
# Create chat
curl -X POST http://localhost:8000/api/chat/create \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Bob"}'

# Send message (replace CHAT_ID with actual ID)
curl -X POST http://localhost:8000/api/chat/CHAT_ID/message \
  -H "Content-Type: application/json" \
  -d '{"user_message":"How do I reset my password?"}'
```

## Assumptions Made

1. **PDF Format**: Knowledge base stored as PDFs in the `data/` folder
2. **Vector Database**: Using ChromaDB for semantic search (can be swapped)
3. **LLM Provider**: Using OpenAI API (GPT-3.5-turbo/GPT-4)
4. **Ticket System**: Mock implementation simulating Jira (easily replaceable)
5. **Authentication**: Not implemented (add for production)
6. **Session Storage**: In-memory (use Redis/PostgreSQL for production)
7. **Scale**: Designed for single-server (use distributed task queue for scale)

## File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application and routes |
| `knowledge_base.py` | ChromaDB setup and PDF ingestion |
| `ticket_system.py` | Mock Jira-like ticket management |
| `support_agent.py` | LangChain agent orchestration |
| `config.py` | Configuration and constants |

## Future Enhancements

- [ ] Real Jira/ZenDesk integration
- [ ] Database persistence (PostgreSQL)
- [ ] Redis for caching and sessions
- [ ] WebSocket for real-time chat
- [ ] Rate limiting and authentication
- [ ] Admin dashboard
- [ ] Analytics and metrics
- [ ] Multi-language support
- [ ] Custom fine-tuned models
- [ ] Sentiment analysis integration

## Troubleshooting

### Issue: "No module named 'chromadb'"
**Solution**: Run `pip install -r requirements.txt` again

### Issue: "OpenAI API key not found"
**Solution**: Check `.env` file has `OPENAI_API_KEY` set correctly

### Issue: "No PDF files found"
**Solution**: Ensure PDF files are in `data/` folder and run `/api/kb/initialize` endpoint

### Issue: Knowledge base not responding to queries
**Solution**: Run POST `/api/kb/initialize` to re-index PDFs

## Mock Data Included

The system includes mock tickets for testing:
- TICKET-001: "Cannot access account" (High Priority)
- TICKET-002: "Product issues" (Medium Priority)
- TICKET-003: "Billing inquiry" (Low Priority)

These can be queried via `/api/tickets/{ticket_id}` endpoint.

## Performance Considerations

- **First request**: May be slower (model initialization)
- **Knowledge base queries**: <1s typical response
- **Agent processing**: 2-5s average
- **Batch operations**: Consider async processing

## Monitoring & Logging

Logs are printed to console. For production:
- Use structured logging (ELK stack)
- Add metrics collection (Prometheus)
- Monitor API latency and errors

## References

- [ChromaDB Documentation](https://docs.trychroma.com)
- [LangChain Documentation](https://python.langchain.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API Reference](https://platform.openai.com/docs)
