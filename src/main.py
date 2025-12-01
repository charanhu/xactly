# main.py
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from knowledge_base import KnowledgeBase
from ticket_system import TicketSystem
from support_agent import SupportAgent
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Agent",
    description="AI-powered customer support agent with knowledge base and ticket system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
kb = KnowledgeBase()
tickets = TicketSystem()
agent = SupportAgent(kb, tickets)

# Request/Response models
class InitializeKBRequest(BaseModel):
    """Request to initialize knowledge base."""
    clear_existing: bool = False


class CreateChatRequest(BaseModel):
    """Request to create a new chat session."""
    customer_name: str
    ticket_id: Optional[str] = None


class CreateChatResponse(BaseModel):
    """Response when creating a new chat."""
    chat_id: str
    customer_name: str
    ticket_id: Optional[str] = None
    message: str
    timestamp: str


class SendMessageRequest(BaseModel):
    """Request to send a message."""
    user_message: str


class SendMessageResponse(BaseModel):
    """Response to a message."""
    chat_id: str
    agent_response: str
    kb_sources: List[dict]
    ticket_info: Optional[dict] = None
    timestamp: str


class ChatMessage(BaseModel):
    """A message in the chat history."""
    role: str
    message: str


# In-memory chat sessions storage
chat_sessions = {}


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Customer Support Agent...")
    logger.info(f"OpenAI Model: {config.GROQ_MODEL}")
    logger.info(f"Data Folder: {config.DATA_FOLDER}")
    logger.info(f"ChromaDB Path: {config.CHROMA_DB_PATH}")
    logger.info("Application started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "kb_status": kb.get_collection_info(),
        "active_chats": len(chat_sessions)
    }


@app.post("/api/kb/initialize")
async def initialize_knowledge_base(request: InitializeKBRequest = Body(default={"clear_existing": False})):
    """
    Initialize the knowledge base by loading PDFs.
    
    Args:
        request: Initialization request with optional clear flag
        
    Returns:
        Initialization status
    """
    try:
        logger.info("Initializing knowledge base...")
        
        if request.clear_existing:
            logger.info("Clearing existing knowledge base...")
            kb.clear_knowledge_base()
        
        result = kb.initialize_knowledge_base()
        logger.info(f"Knowledge base initialization result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kb/info")
async def get_kb_info():
    """Get information about the knowledge base."""
    try:
        return kb.get_collection_info()
    except Exception as e:
        logger.error(f"Error getting KB info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/create", response_model=CreateChatResponse)
async def create_chat(request: CreateChatRequest):
    """
    Create a new customer support chat session.
    
    Args:
        request: Chat creation request
        
    Returns:
        Chat session details
    """
    try:
        chat_id = str(uuid.uuid4())
        
        # Store session
        chat_sessions[chat_id] = {
            "customer_name": request.customer_name,
            "ticket_id": request.ticket_id,
            "created_at": datetime.now(),
            "messages": []
        }
        
        logger.info(f"Created chat session: {chat_id} for {request.customer_name}")
        
        greeting = f"Hello {request.customer_name}! I'm your AI support agent. How can I help you today?"
        if request.ticket_id:
            greeting += f" I see you have ticket {request.ticket_id} associated with this chat."
        
        return CreateChatResponse(
            chat_id=chat_id,
            customer_name=request.customer_name,
            ticket_id=request.ticket_id,
            message=greeting,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/{chat_id}/message", response_model=SendMessageResponse)
async def send_message(chat_id: str, request: SendMessageRequest):
    """
    Send a message in a chat session and get an AI response.
    
    Args:
        chat_id: Chat session ID
        request: Message request
        
    Returns:
        Agent response with sources
    """
    try:
        # Validate chat session exists
        if chat_id not in chat_sessions:
            raise HTTPException(status_code=404, detail=f"Chat session {chat_id} not found")
        
        session = chat_sessions[chat_id]
        ticket_id = session.get("ticket_id")
        
        # Process message through agent
        logger.info(f"Processing message for chat {chat_id}")
        result = agent.process_message(
            user_message=request.user_message,
            chat_id=chat_id,
            ticket_id=ticket_id
        )
        
        # Store in session
        session["messages"].append({
            "role": "user",
            "message": request.user_message,
            "timestamp": datetime.now().isoformat()
        })
        session["messages"].append({
            "role": "assistant",
            "message": result["agent_response"],
            "timestamp": datetime.now().isoformat()
        })
        
        return SendMessageResponse(
            chat_id=chat_id,
            agent_response=result["agent_response"],
            kb_sources=result["kb_sources"],
            ticket_info=result["ticket_info"],
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/{chat_id}/history")
async def get_chat_history(chat_id: str):
    """
    Get the chat history for a session.
    
    Args:
        chat_id: Chat session ID
        
    Returns:
        List of messages in the chat
    """
    try:
        if chat_id not in chat_sessions:
            raise HTTPException(status_code=404, detail=f"Chat session {chat_id} not found")
        
        session = chat_sessions[chat_id]
        return {
            "chat_id": chat_id,
            "customer_name": session["customer_name"],
            "ticket_id": session.get("ticket_id"),
            "created_at": session["created_at"].isoformat(),
            "messages": session["messages"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/{chat_id}/clear")
async def clear_chat(chat_id: str):
    """
    Clear the conversation history for a chat.
    
    Args:
        chat_id: Chat session ID
        
    Returns:
        Status message
    """
    try:
        if chat_id not in chat_sessions:
            raise HTTPException(status_code=404, detail=f"Chat session {chat_id} not found")
        
        agent.clear_chat_history(chat_id)
        chat_sessions[chat_id]["messages"] = []
        
        logger.info(f"Cleared chat history for {chat_id}")
        return {
            "status": "success",
            "message": f"Chat history cleared for {chat_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket information.
    
    Args:
        ticket_id: The ticket ID
        
    Returns:
        Ticket details
    """
    try:
        ticket = tickets.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets")
async def list_tickets():
    """Get all available tickets."""
    try:
        return {
            "total": len(tickets.get_all_tickets()),
            "tickets": tickets.get_all_tickets()
        }
    except Exception as e:
        logger.error(f"Error listing tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats")
async def list_active_chats():
    """Get list of active chat sessions."""
    try:
        return {
            "total": len(chat_sessions),
            "chats": [
                {
                    "chat_id": chat_id,
                    "customer_name": session["customer_name"],
                    "ticket_id": session.get("ticket_id"),
                    "created_at": session["created_at"].isoformat(),
                    "message_count": len(session["messages"])
                }
                for chat_id, session in chat_sessions.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error listing chats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/kb/search")
async def search_knowledge_base(query: str = Body(..., embed=True)):
    """
    Search the knowledge base directly.
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    try:
        results = kb.search(query)
        return {
            "query": query,
            "results_count": len(results),
            "results": [
                {
                    "document": doc[:500] + "..." if len(doc) > 500 else doc,
                    "source": metadata.get("source", "Unknown"),
                    "page": metadata.get("page", "N/A"),
                    "similarity": f"{similarity:.1%}"
                }
                for doc, metadata, similarity in results
            ]
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
