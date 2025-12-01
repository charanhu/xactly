# ticket_system.py
import logging
from typing import Optional, List, Dict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Mock ticket database
TICKETS_DB = {
    "TICKET-001": {
        "ticket_id": "TICKET-001",
        "customer_name": "Alice Johnson",
        "status": "open",
        "priority": "high",
        "created_date": "2024-11-25",
        "title": "Cannot access account",
        "description": "User unable to log in. Getting 'Invalid credentials' error.",
        "category": "account",
        "assigned_to": "Support Team"
    },
    "TICKET-002": {
        "ticket_id": "TICKET-002",
        "customer_name": "Bob Smith",
        "status": "open",
        "priority": "medium",
        "created_date": "2024-11-28",
        "title": "Product not working as expected",
        "description": "Application crashes when uploading large files.",
        "category": "product",
        "assigned_to": "Support Team"
    },
    "TICKET-003": {
        "ticket_id": "TICKET-003",
        "customer_name": "Charlie Brown",
        "status": "resolved",
        "priority": "low",
        "created_date": "2024-11-20",
        "title": "Billing inquiry",
        "description": "Question about recent invoice charges.",
        "category": "billing",
        "assigned_to": "Billing Team"
    }
}

class TicketSystem:
    """Manages customer support tickets (simulates Jira/similar systems)."""
    
    def __init__(self):
        """Initialize ticket system."""
        self.tickets = TICKETS_DB.copy()
        logger.info("Ticket System initialized")
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Retrieve a ticket by ID.
        
        Args:
            ticket_id: The ticket identifier
            
        Returns:
            Ticket details or None if not found
        """
        ticket = self.tickets.get(ticket_id)
        if ticket:
            logger.info(f"Retrieved ticket: {ticket_id}")
        else:
            logger.warning(f"Ticket not found: {ticket_id}")
        return ticket
    
    def create_ticket(self, customer_name: str, title: str, description: str, 
                     category: str = "general", priority: str = "medium") -> str:
        """
        Create a new ticket.
        
        Args:
            customer_name: Name of the customer
            title: Ticket title
            description: Ticket description
            category: Ticket category
            priority: Ticket priority (low/medium/high/critical)
            
        Returns:
            New ticket ID
        """
        ticket_id = f"TICKET-{len(self.tickets) + 1:03d}"
        
        ticket = {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "status": "open",
            "priority": priority,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "title": title,
            "description": description,
            "category": category,
            "assigned_to": "Support Team"
        }
        
        self.tickets[ticket_id] = ticket
        logger.info(f"Created new ticket: {ticket_id}")
        return ticket_id
    
    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """
        Update ticket status.
        
        Args:
            ticket_id: The ticket ID
            status: New status (open/in_progress/resolved/closed)
            
        Returns:
            True if successful, False otherwise
        """
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            logger.info(f"Updated ticket {ticket_id} status to {status}")
            return True
        return False
    
    def get_customer_tickets(self, customer_name: str) -> List[Dict]:
        """
        Get all tickets for a customer.
        
        Args:
            customer_name: Customer name to search
            
        Returns:
            List of tickets for the customer
        """
        tickets = [t for t in self.tickets.values() 
                  if t["customer_name"].lower() == customer_name.lower()]
        logger.info(f"Found {len(tickets)} tickets for customer: {customer_name}")
        return tickets
    
    def get_open_tickets(self) -> List[Dict]:
        """Get all open tickets."""
        tickets = [t for t in self.tickets.values() if t["status"] == "open"]
        return tickets
    
    def add_ticket_note(self, ticket_id: str, note: str) -> bool:
        """
        Add a note to a ticket.
        
        Args:
            ticket_id: The ticket ID
            note: Note text
            
        Returns:
            True if successful, False otherwise
        """
        if ticket_id in self.tickets:
            if "notes" not in self.tickets[ticket_id]:
                self.tickets[ticket_id]["notes"] = []
            
            self.tickets[ticket_id]["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "text": note
            })
            logger.info(f"Added note to ticket {ticket_id}")
            return True
        return False
    
    def search_tickets(self, query: str) -> List[Dict]:
        """
        Search tickets by title or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tickets
        """
        query_lower = query.lower()
        results = [
            t for t in self.tickets.values()
            if query_lower in t["title"].lower() or 
               query_lower in t["description"].lower()
        ]
        logger.info(f"Found {len(results)} tickets matching query: {query}")
        return results
    
    def get_ticket_summary(self, ticket_id: str) -> str:
        """Get a formatted summary of a ticket."""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return f"Ticket {ticket_id} not found"
        
        summary = f"""
Ticket ID: {ticket['ticket_id']}
Title: {ticket['title']}
Status: {ticket['status']}
Priority: {ticket['priority']}
Category: {ticket['category']}
Customer: {ticket['customer_name']}
Created: {ticket['created_date']}
Description: {ticket['description']}
Assigned To: {ticket['assigned_to']}
"""
        return summary.strip()
    
    def get_all_tickets(self) -> List[Dict]:
        """Get all tickets."""
        return list(self.tickets.values())
