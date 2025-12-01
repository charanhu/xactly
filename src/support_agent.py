# support_agent.py
import logging
from typing import List, Tuple, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.messages import HumanMessage, AIMessage
from knowledge_base import KnowledgeBase
from ticket_system import TicketSystem
import config
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY


class SupportAgent:
    """AI agent for customer support with knowledge base and ticket access."""

    def __init__(self, knowledge_base: KnowledgeBase, ticket_system: TicketSystem):
        """
        Initialize the support agent.

        Args:
            knowledge_base: KnowledgeBase instance
            ticket_system: TicketSystem instance
        """
        self.kb = knowledge_base
        self.tickets = ticket_system

        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=config.GROQ_API_KEY,
        )

        # Conversation history storage
        self.conversation_history = {}

        logger.info("Support Agent initialized")

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the support agent."""
        return """You are a helpful and professional customer support agent. Your role is to:

1. Listen to customer issues and concerns
2. Search the knowledge base for relevant information
3. Access ticket information if provided
4. Provide clear, accurate, and helpful responses
5. Be empathetic and professional
6. Offer solutions or escalation when needed

When responding:
- Be concise but thorough
- Reference specific information from the knowledge base when applicable
- Maintain the context of the conversation
- If you don't know something, say so and offer to help find the answer
- Always be polite and professional

The customer may reference a ticket ID. Use this to provide personalized support based on their existing issue history."""

    def _search_knowledge_base(self, query: str) -> List[Tuple[str, Dict, float]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: Search query

        Returns:
            List of (document, metadata, similarity) tuples
        """
        logger.info(f"Searching knowledge base for: {query}")
        results = self.kb.search(query, n_results=config.KB_SEARCH_RESULTS)
        logger.info(f"Found {len(results)} knowledge base results")

        # Convert Document objects to (text, metadata, score) tuples
        formatted_results = []
        for doc, similarity in results:
            formatted_results.append((doc.page_content, doc.metadata, similarity))

        return formatted_results

    def _format_kb_context(self, kb_results: List[Tuple[str, Dict, float]]) -> str:
        """
        Format knowledge base search results into context.

        Args:
            kb_results: Knowledge base search results

        Returns:
            Formatted context string
        """
        if not kb_results:
            return ""

        context = "\n\nRelevant Information from Knowledge Base:\n"
        context += "=" * 50 + "\n"

        for i, (doc, metadata, similarity) in enumerate(kb_results, 1):
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "N/A")
            context += f"\n[Source {i}] {source} (Page {page})\n"
            context += f"Relevance: {similarity:.1%}\n"
            context += (
                f"Content: {doc[:500]}...\n" if len(doc) > 500 else f"Content: {doc}\n"
            )

        return context

    def _get_ticket_context(self, ticket_id: str) -> str:
        """
        Get ticket information as context.

        Args:
            ticket_id: Ticket ID to retrieve

        Returns:
            Formatted ticket information
        """
        ticket = self.tickets.get_ticket(ticket_id)
        if not ticket:
            return ""

        context = "\n\nTicket Information:\n"
        context += "=" * 50 + "\n"
        context += self.tickets.get_ticket_summary(ticket_id)
        return context

    def process_message(
        self, user_message: str, chat_id: str, ticket_id: Optional[str] = None
    ) -> Dict:
        """
        Process a user message and generate an agent response.

        Args:
            user_message: The user's message
            chat_id: Unique chat session ID
            ticket_id: Optional ticket ID for context

        Returns:
            Dictionary with agent response and metadata
        """
        logger.info(f"Processing message for chat {chat_id}: {user_message[:100]}")

        # Initialize conversation history for this chat if needed
        if chat_id not in self.conversation_history:
            self.conversation_history[chat_id] = []

        # Search knowledge base
        kb_results = self._search_knowledge_base(user_message)
        kb_context = self._format_kb_context(kb_results)

        # Get ticket context if provided
        ticket_context = ""
        ticket_info = None
        if ticket_id:
            ticket_info = self.tickets.get_ticket(ticket_id)
            ticket_context = self._get_ticket_context(ticket_id)

        # Build the prompt
        system_prompt = self._create_system_prompt()

        full_context = ""
        if ticket_context:
            full_context += ticket_context
        if kb_context:
            full_context += kb_context

        # Create messages for the LLM
        messages = []

        # Add system message
        messages.append(("system", system_prompt + full_context))

        # Add conversation history
        for role, content in self.conversation_history[chat_id]:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        # Get response from LLM
        try:
            response = self.llm.invoke(messages)
            agent_response = response.content
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            agent_response = "I apologize, but I encountered an error processing your request. Please try again."

        # Update conversation history
        self.conversation_history[chat_id].append(("user", user_message))
        self.conversation_history[chat_id].append(("assistant", agent_response))

        # Keep only recent history
        if len(self.conversation_history[chat_id]) > config.MAX_CHAT_HISTORY:
            self.conversation_history[chat_id] = self.conversation_history[chat_id][
                -config.MAX_CHAT_HISTORY :
            ]

        # Format KB sources
        kb_sources = [
            {
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page", "N/A"),
                "similarity": f"{similarity:.1%}",
                "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
            }
            for doc, metadata, similarity in kb_results
        ]

        return {
            "agent_response": agent_response,
            "kb_sources": kb_sources,
            "ticket_info": ticket_info,
            "conversation_length": len(self.conversation_history[chat_id]),
        }

    def get_chat_history(self, chat_id: str) -> List[Dict]:
        """
        Get the conversation history for a chat.

        Args:
            chat_id: Chat session ID

        Returns:
            List of messages with role and content
        """
        history = []
        if chat_id in self.conversation_history:
            for role, content in self.conversation_history[chat_id]:
                history.append({"role": role, "message": content})
        return history

    def clear_chat_history(self, chat_id: str) -> bool:
        """
        Clear the conversation history for a chat.

        Args:
            chat_id: Chat session ID

        Returns:
            True if successful
        """
        if chat_id in self.conversation_history:
            del self.conversation_history[chat_id]
            logger.info(f"Cleared conversation history for chat {chat_id}")
            return True
        return False
