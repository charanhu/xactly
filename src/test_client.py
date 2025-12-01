# test_client.py
"""
Test client for the Customer Support Agent API.
Run this to test the full workflow without needing the UI.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2))


def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response.json())


def test_initialize_kb():
    """Initialize knowledge base."""
    response = requests.post(f"{BASE_URL}/api/kb/initialize")
    print_response("Initialize Knowledge Base", response.json())


def test_kb_info():
    """Get knowledge base info."""
    response = requests.get(f"{BASE_URL}/api/kb/info")
    print_response("Knowledge Base Info", response.json())


def test_list_tickets():
    """List all available tickets."""
    response = requests.get(f"{BASE_URL}/api/tickets")
    print_response("List Tickets", response.json())


def test_get_ticket(ticket_id="TICKET-001"):
    """Get specific ticket info."""
    response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}")
    print_response(f"Get Ticket {ticket_id}", response.json())


def test_create_chat(customer_name="Test Customer", ticket_id=None):
    """Create a new chat session."""
    payload = {"customer_name": customer_name}
    if ticket_id:
        payload["ticket_id"] = ticket_id
    
    response = requests.post(f"{BASE_URL}/api/chat/create", json=payload)
    result = response.json()
    print_response("Create Chat", result)
    return result.get("chat_id")


def test_send_message(chat_id, user_message):
    """Send a message and get agent response."""
    payload = {"user_message": user_message}
    response = requests.post(f"{BASE_URL}/api/chat/{chat_id}/message", json=payload)
    print_response(f"Send Message", response.json())


def test_chat_history(chat_id):
    """Get chat history."""
    response = requests.get(f"{BASE_URL}/api/chat/{chat_id}/history")
    print_response("Chat History", response.json())


def test_active_chats():
    """List active chats."""
    response = requests.get(f"{BASE_URL}/api/chats")
    print_response("Active Chats", response.json())


def test_kb_search(query):
    """Search knowledge base."""
    response = requests.post(f"{BASE_URL}/api/kb/search", json=query)
    print_response(f"Knowledge Base Search: {query}", response.json())


def run_full_test():
    """Run full test workflow."""
    print("\n" + "="*60)
    print("CUSTOMER SUPPORT AGENT - FULL TEST WORKFLOW")
    print("="*60)
    
    # 1. Health check
    print("\n[1/8] Checking health...")
    test_health_check()
    sleep(1)
    
    # 2. Initialize KB
    print("\n[2/8] Initializing knowledge base...")
    test_initialize_kb()
    sleep(2)
    
    # 3. Get KB info
    print("\n[3/8] Getting knowledge base info...")
    test_kb_info()
    sleep(1)
    
    # 4. List tickets
    print("\n[4/8] Listing available tickets...")
    test_list_tickets()
    sleep(1)
    
    # 5. Get specific ticket
    print("\n[5/8] Getting specific ticket info...")
    test_get_ticket("TICKET-001")
    sleep(1)
    
    # 6. Create chat with ticket
    print("\n[6/8] Creating chat session with ticket reference...")
    chat_id = test_create_chat("John Doe", "TICKET-001")
    sleep(1)
    
    if chat_id:
        # 7. Send messages
        print("\n[7/8] Sending messages to agent...")
        test_send_message(chat_id, "I can't seem to log into my account. I'm getting an error message.")
        sleep(2)
        
        test_send_message(chat_id, "What's the typical resolution time for this type of issue?")
        sleep(2)
        
        # 8. Get chat history
        print("\n[8/8] Retrieving chat history...")
        test_chat_history(chat_id)
    
    # Show active chats
    print("\n[BONUS] Listing all active chats...")
    test_active_chats()
    
    print("\n" + "="*60)
    print("TEST WORKFLOW COMPLETED!")
    print("="*60)


def interactive_mode():
    """Run in interactive mode."""
    print("\n" + "="*60)
    print("CUSTOMER SUPPORT AGENT - INTERACTIVE MODE")
    print("="*60)
    
    # Initialize KB
    print("\nInitializing knowledge base...")
    test_initialize_kb()
    sleep(2)
    
    # Create chat
    customer_name = input("\nEnter your name: ").strip() or "Guest"
    use_ticket = input("Do you have a ticket ID? (y/n): ").strip().lower() == 'y'
    ticket_id = None
    
    if use_ticket:
        print("\nAvailable tickets:")
        test_list_tickets()
        ticket_id = input("\nEnter ticket ID: ").strip() or None
    
    chat_id = test_create_chat(customer_name, ticket_id)
    sleep(1)
    
    if chat_id:
        print(f"\nChat started! Chat ID: {chat_id}")
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'history' to see chat history")
        print("-" * 60)
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'history':
                test_chat_history(chat_id)
                continue
            elif not user_input:
                continue
            
            test_send_message(chat_id, user_input)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_mode()
        elif sys.argv[1] == "search":
            query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "help with product issues"
            test_kb_search(query)
        else:
            print("Unknown command")
    else:
        # Run full test by default
        try:
            run_full_test()
        except requests.exceptions.ConnectionError:
            print("\nError: Could not connect to API server!")
            print("Make sure the server is running: python main.py")
        except Exception as e:
            print(f"\nError: {str(e)}")
