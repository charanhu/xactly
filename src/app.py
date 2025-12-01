import streamlit as st
import time
import logging
import sys
import os
from datetime import datetime

# Import your existing modules
from ticket_system import TicketSystem
from support_agent import SupportAgent
from knowledge_base import KnowledgeBase
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for better UI ---
st.markdown("""
<style>
    /* Main chat container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .info-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    /* Ticket badge */
    .ticket-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .status-open { background-color: #fef3c7; color: #92400e; }
    .status-resolved { background-color: #d1fae5; color: #065f46; }
    .priority-high { background-color: #fee2e2; color: #991b1b; }
    .priority-medium { background-color: #fed7aa; color: #9a3412; }
    .priority-low { background-color: #dbeafe; color: #1e40af; }
    .priority-critical { background-color: #fecaca; color: #7f1d1d; }
    
    /* Relevance indicator */
    .relevance-high { color: #059669; font-weight: bold; }
    .relevance-medium { color: #d97706; font-weight: bold; }
    .relevance-low { color: #6b7280; font-weight: bold; }
    
    /* Chat input area */
    .stChatInputContainer {
        border-top: 2px solid #e5e7eb;
        padding-top: 1rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f9fafb;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def parse_similarity(similarity_str):
    """Parse similarity string and return a normalized float between 0 and 1."""
    try:
        # Remove '%' if present and convert to float
        if isinstance(similarity_str, str):
            value = float(similarity_str.strip('%')) / 100
        else:
            value = float(similarity_str)
        
        # Clamp value between 0 and 1
        return max(0.0, min(1.0, value))
    except (ValueError, TypeError):
        return 0.0

def get_relevance_class(similarity_value):
    """Get CSS class based on similarity score."""
    if similarity_value >= 0.7:
        return "relevance-high"
    elif similarity_value >= 0.4:
        return "relevance-medium"
    else:
        return "relevance-low"

def get_relevance_emoji(similarity_value):
    """Get emoji based on similarity score."""
    if similarity_value >= 0.7:
        return "🟢"
    elif similarity_value >= 0.4:
        return "🟡"
    else:
        return "🔴"

# --- Initialization (Cached Resources) ---
@st.cache_resource
def get_system_components():
    """Initialize the backend components once and cache them."""
    try:
        kb = KnowledgeBase()
        tickets = TicketSystem()
        agent = SupportAgent(kb, tickets)
        return kb, tickets, agent
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return None, None, None

kb, tickets, agent = get_system_components()

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = f"chat_{int(time.time())}"
if "current_ticket_id" not in st.session_state:
    st.session_state.current_ticket_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "kb_initialized" not in st.session_state:
    st.session_state.kb_initialized = False

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/chat.png", width=100)
    st.title("🤖 AI Support")
    st.markdown("---")
    
    # User Profile Section
    with st.expander("👤 Your Profile", expanded=True):
        new_name = st.text_input("Your Name", value=st.session_state.user_name, key="name_input")
        if new_name != st.session_state.user_name:
            st.session_state.user_name = new_name
            st.success("✓ Name updated!")
    
    # Ticket Selection
    with st.expander("🎫 Select Ticket (Optional)", expanded=False):
        all_tickets = tickets.get_all_tickets()
        
        ticket_options = ["None"] + [f"{t['ticket_id']} - {t['title']}" for t in all_tickets]
        
        current_selection = "None"
        if st.session_state.current_ticket_id:
            for opt in ticket_options:
                if st.session_state.current_ticket_id in opt:
                    current_selection = opt
                    break
        
        selected = st.selectbox(
            "Choose existing ticket",
            ticket_options,
            index=ticket_options.index(current_selection),
            key="ticket_select"
        )
        
        if selected != "None":
            ticket_id = selected.split(" - ")[0]
            if ticket_id != st.session_state.current_ticket_id:
                st.session_state.current_ticket_id = ticket_id
                ticket_info = tickets.get_ticket(ticket_id)
                if ticket_info:
                    st.session_state.user_name = ticket_info['customer_name']
                st.success(f"✓ Ticket {ticket_id} selected!")
                st.rerun()
        else:
            if st.session_state.current_ticket_id is not None:
                st.session_state.current_ticket_id = None
                st.rerun()
    
    # Display current ticket info
    if st.session_state.current_ticket_id:
        ticket = tickets.get_ticket(st.session_state.current_ticket_id)
        if ticket:
            st.info(f"**Active Ticket:** {ticket['ticket_id']}\n\n"
                   f"**Status:** {ticket['status'].upper()}\n\n"
                   f"**Priority:** {ticket['priority'].upper()}")
    
    st.markdown("---")
    
    # Knowledge Base Management
    with st.expander("📚 Knowledge Base", expanded=False):
        if st.button("🔄 Initialize KB", use_container_width=True):
            with st.spinner("Loading documents..."):
                try:
                    status = kb.initialize_knowledge_base()
                    st.session_state.kb_initialized = True
                    st.success(f"✓ Loaded {status.get('docs_loaded', 0)} documents!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        kb_info = kb.get_collection_info()
        st.metric("Documents in KB", kb_info.get('document_count', 0))
    
    # Chat Controls
    with st.expander("⚙️ Chat Controls", expanded=False):
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            agent.clear_chat_history(st.session_state.chat_id)
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.success("✓ Chat cleared!")
            st.rerun()
        
        if st.button("🔄 New Chat Session", use_container_width=True):
            st.session_state.chat_id = f"chat_{int(time.time())}"
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.success("✓ New session started!")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"🤖 Model: {config.GROQ_MODEL}")
    st.caption(f"💬 Chat ID: {st.session_state.chat_id[:8]}...")

# --- Main Content Area ---

# Welcome Screen (shown when no messages)
if not st.session_state.messages:
    st.markdown("""
    <div class="main-header">
        <h1>👋 Welcome to AI Customer Support</h1>
        <p>I'm here to help you with any questions or issues. Just type your message below to get started!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Start Guide
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🎯 How It Works</h3>
            <p>1. Enter your name in the sidebar<br>
            2. Optionally select a ticket<br>
            3. Type your question below<br>
            4. Get instant AI-powered help!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>💡 What I Can Help With</h3>
            <p>• Account access issues<br>
            • Technical troubleshooting<br>
            • Billing questions<br>
            • General product support</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>⚡ Quick Tips</h3>
            <p>• Be specific about your issue<br>
            • Reference ticket IDs if available<br>
            • Check the sources for details<br>
            • Ask follow-up questions anytime</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample Questions
    st.markdown("### 💬 Try asking something like:")
    
    sample_col1, sample_col2 = st.columns(2)
    
    with sample_col1:
        if st.button("🔐 How do I reset my password?", use_container_width=True):
            st.session_state.sample_question = "How do I reset my password?"
            st.rerun()
        if st.button("💳 What payment methods do you accept?", use_container_width=True):
            st.session_state.sample_question = "What payment methods do you accept?"
            st.rerun()
    
    with sample_col2:
        if st.button("🚀 How do I upgrade my plan?", use_container_width=True):
            st.session_state.sample_question = "How do I upgrade my plan?"
            st.rerun()
        if st.button("📧 I'm not receiving verification emails", use_container_width=True):
            st.session_state.sample_question = "I'm not receiving verification emails"
            st.rerun()

# Chat Interface
else:
    # Header with current context
    header_col1, header_col2, header_col3 = st.columns([2, 2, 1])
    
    with header_col1:
        st.markdown(f"### 💬 Chat with AI Support")
    
    with header_col2:
        if st.session_state.current_ticket_id:
            st.markdown(f"**🎫 Ticket:** `{st.session_state.current_ticket_id}`")
    
    with header_col3:
        st.markdown(f"**👤** {st.session_state.user_name}")
    
    st.markdown("---")
    
    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            
            # Show sources in a cleaner way
            if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
                with st.expander("📚 View Sources & References", expanded=False):
                    for idx, source in enumerate(msg["sources"], 1):
                        # Parse similarity safely
                        similarity_value = parse_similarity(source.get('similarity', '0%'))
                        relevance_emoji = get_relevance_emoji(similarity_value)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{idx}. {source['source']}** (Page {source['page']})")
                            st.caption(f"_{source.get('excerpt', 'No excerpt available')}_")
                        
                        with col2:
                            st.markdown(f"{relevance_emoji} **{similarity_value:.0%}**")
                            st.caption("Relevance")
                        
                        if idx < len(msg["sources"]):
                            st.divider()

# Chat Input (always at bottom)
st.markdown("---")

# Handle sample question
if "sample_question" in st.session_state:
    prompt = st.session_state.sample_question
    del st.session_state.sample_question
else:
    prompt = st.chat_input("💬 Type your message here...", key="chat_input")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_started = True
    
    # Rerun to show user message
    st.rerun()

# Process last message if it's from user and needs response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            try:
                response_data = agent.process_message(
                    user_message=st.session_state.messages[-1]["content"],
                    chat_id=st.session_state.chat_id,
                    ticket_id=st.session_state.current_ticket_id
                )
                
                agent_msg = response_data["agent_response"]
                sources = response_data.get("kb_sources", [])
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_msg,
                    "sources": sources
                })
                
                st.rerun()
                
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })
                st.rerun()

# Quick Actions Footer
if st.session_state.messages:
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        if st.button("📋 View All Tickets", use_container_width=True):
            st.session_state.show_tickets = True
    
    with footer_col2:
        if st.button("🔍 Search Knowledge Base", use_container_width=True):
            st.session_state.show_kb_search = True
    
    with footer_col3:
        message_count = len(st.session_state.messages)
        st.metric("Messages", f"{message_count}")

# Modals for additional features
if "show_tickets" in st.session_state and st.session_state.show_tickets:
    with st.expander("🎫 All Tickets", expanded=True):
        all_tickets = tickets.get_all_tickets()
        for t in all_tickets:
            col1, col2 = st.columns([4, 1])
            with col1:
                status_class = f"status-{t['status']}"
                priority_class = f"priority-{t['priority']}"
                st.markdown(f"""
                **{t['ticket_id']}**: {t['title']}  
                <span class="ticket-badge {status_class}">{t['status'].upper()}</span>
                <span class="ticket-badge {priority_class}">{t['priority'].upper()}</span>  
                Customer: {t['customer_name']} | Created: {t['created_date']}
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Select", key=f"select_{t['ticket_id']}", use_container_width=True):
                    st.session_state.current_ticket_id = t['ticket_id']
                    st.session_state.user_name = t['customer_name']
                    st.session_state.show_tickets = False
                    st.rerun()
            st.divider()
        
        if st.button("Close", use_container_width=True):
            st.session_state.show_tickets = False
            st.rerun()

if "show_kb_search" in st.session_state and st.session_state.show_kb_search:
    with st.expander("🔍 Search Knowledge Base", expanded=True):
        search_query = st.text_input("Enter your search query:", key="kb_search_input")
        
        if search_query:
            with st.spinner("Searching..."):
                results = kb.search(search_query)
                st.success(f"Found {len(results)} results")
                
                for doc, score in results:
                    # Normalize score safely
                    normalized_score = max(0.0, min(1.0, float(score)))
                    relevance_emoji = get_relevance_emoji(normalized_score)
                    
                    st.markdown(f"{relevance_emoji} **Relevance: {normalized_score:.1%}**")
                    st.info(doc.page_content[:300] + "...")
                    st.caption(f"Source: {doc.metadata.get('source', 'Unknown')} | Page: {doc.metadata.get('page', 'N/A')}")
                    st.divider()
        
        if st.button("Close", use_container_width=True):
            st.session_state.show_kb_search = False
            st.rerun()
