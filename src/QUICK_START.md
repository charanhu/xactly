# QUICK_START.md

## Quick Start Guide - Customer Support Agent

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- OpenAI API key (get from https://platform.openai.com/api-keys)

---

## 5-Minute Setup

### Step 1: Clone and Setup Environment
```bash
# Create project directory
mkdir customer-support-agent
cd customer-support-agent

# Copy all files to this directory
# (main.py, config.py, knowledge_base.py, ticket_system.py, support_agent.py)

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Add Knowledge Base (Optional)
```bash
# Create data folder
mkdir data

# Add your PDF files to the data/ folder
# Example: data/company-policies.pdf, data/faq.pdf
```

### Step 4: Start the Server
```bash
python main.py
```

Expected output:
```
INFO:uvicorn.server:Uvicorn running on http://0.0.0.0:8000
```

---

## Testing the Agent

### Option A: Using Swagger UI (Visual)
1. Open browser: http://localhost:8000/docs
2. Click "Try it out" on endpoints
3. Start with `/api/kb/initialize` to load PDFs
4. Create chat via `/api/chat/create`
5. Send messages via `/api/chat/{chat_id}/message`

### Option B: Using Python Test Client
```bash
# In a new terminal (keep server running)
python test_client.py

# Run interactive mode
python test_client.py interactive

# Search knowledge base
python test_client.py search "account login issues"
```

### Option C: Using cURL
```bash
# Check health
curl http://localhost:8000/health

# Initialize KB
curl -X POST http://localhost:8000/api/kb/initialize

# Create chat
curl -X POST http://localhost:8000/api/chat/create \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"John Doe","ticket_id":"TICKET-001"}'

# Send message (replace CHAT_ID with actual ID)
curl -X POST http://localhost:8000/api/chat/{CHAT_ID}/message \
  -H "Content-Type: application/json" \
  -d '{"user_message":"I cannot log in to my account"}'
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'chromadb'"
**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Issue 2: "OPENAI_API_KEY not found"
**Solution**:
1. Check `.env` file exists
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Get key from https://platform.openai.com/api-keys

### Issue 3: "No PDF files found in data folder"
**Solution**:
1. Create `data/` folder if it doesn't exist
2. Add PDF files to the folder
3. Call `/api/kb/initialize` endpoint
4. Check logs for loading status

### Issue 4: LLM responses are slow or timing out
**Solution**:
1. Check OpenAI API status: https://status.openai.com
2. Verify internet connection
3. Try with smaller PDFs first
4. Check rate limits: https://platform.openai.com/account/billing/overview

### Issue 5: Port 8000 already in use
**Solution**:
```bash
# Use different port
uvicorn main:app --port 8001 --reload

# Or kill existing process
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Example Workflows

### Workflow 1: Basic Chat Without Ticket
```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Run client
python test_client.py interactive
```

Then:
1. Enter customer name: "Alice"
2. Do you have a ticket? "n"
3. Message: "How do I reset my password?"
4. Get AI response with knowledge base sources

### Workflow 2: Chat With Ticket Reference
```python
# Using Python requests
import requests

BASE = "http://localhost:8000"

# Initialize KB
requests.post(f"{BASE}/api/kb/initialize")

# Create chat with ticket
chat_resp = requests.post(f"{BASE}/api/chat/create", json={
    "customer_name": "Bob",
    "ticket_id": "TICKET-001"
})
chat_id = chat_resp.json()["chat_id"]

# Send message
msg_resp = requests.post(f"{BASE}/api/chat/{chat_id}/message", json={
    "user_message": "Can you check my ticket status?"
})
print(msg_resp.json()["agent_response"])
```

### Workflow 3: Search Knowledge Base Directly
```bash
python test_client.py search "product setup instructions"
```

---

## API Endpoint Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | System health check |
| POST | `/api/kb/initialize` | Load PDFs into KB |
| GET | `/api/kb/info` | KB statistics |
| POST | `/api/kb/search` | Search KB directly |
| POST | `/api/chat/create` | Start new chat |
| POST | `/api/chat/{chat_id}/message` | Send message |
| GET | `/api/chat/{chat_id}/history` | Get chat history |
| GET | `/api/chat/{chat_id}/clear` | Clear chat history |
| GET | `/api/chats` | List active chats |
| GET | `/api/tickets` | List all tickets |
| GET | `/api/tickets/{ticket_id}` | Get ticket details |

---

## Configuration Tweaking

Edit `config.py` to customize:

```python
# Use GPT-4 instead of GPT-3.5-turbo
OPENAI_MODEL = "gpt-4"

# Increase search results
KB_SEARCH_RESULTS = 10

# Adjust chunk size for better search
KB_CHUNK_SIZE = 500  # Default: 1000

# Increase context passed to LLM
MAX_CHAT_HISTORY = 100  # Default: 50

# Adjust response creativity
AGENT_TEMPERATURE = 0.9  # Default: 0.7 (0=factual, 1=creative)
```

---

## Next Steps

1. **Add Your Data**: Put PDF files in `data/` folder
2. **Test Interactions**: Use Swagger UI or test client
3. **Customize Agent**: Edit system prompt in `support_agent.py`
4. **Build UI**: Create web frontend (React/Vue/HTML)
5. **Deploy**: Use Docker or cloud platform
6. **Monitor**: Add logging and metrics
7. **Integrate**: Connect to real Jira/CRM systems

---

## Useful Resources

- **ChromaDB Docs**: https://docs.trychroma.com
- **LangChain Docs**: https://python.langchain.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenAI API**: https://platform.openai.com/docs
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html

---

## Getting Help

1. Check logs: Look for ERROR messages in terminal
2. Test endpoints: Visit http://localhost:8000/docs
3. Verify environment: Check .env file and API key
4. Try examples: Run `test_client.py` or curl commands
5. Read issues: Check GitHub issues for similar problems

---

## Performance Tips

- **Warm up**: Call `/api/kb/initialize` once at startup
- **Batch requests**: Process multiple messages sequentially
- **Cache embeddings**: Store common queries locally
- **Monitor latency**: Check OpenAI API response times
- **Optimize PDFs**: Use smaller, focused documents

---

## Production Checklist

Before deploying to production:

- [ ] Add API authentication (JWT/API keys)
- [ ] Enable HTTPS/TLS
- [ ] Set up rate limiting
- [ ] Use PostgreSQL for sessions
- [ ] Add Redis for caching
- [ ] Configure logging to file/ELK
- [ ] Set up monitoring/alerts
- [ ] Add input validation/sanitization
- [ ] Implement backup strategy
- [ ] Load test the system
- [ ] Create runbooks for incidents
- [ ] Document deployment procedure

---

## Support

For questions or issues:
1. Check README.md for full documentation
2. Review ASSUMPTIONS_AND_ARCHITECTURE.md for design details
3. Check test_client.py for example usage
4. Examine config.py for all available settings
