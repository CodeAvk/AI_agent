import os
from livekit import rtc
import threading
import asyncio
from datetime import datetime
from flask import current_app
from db.models import db, HelpRequest, KnowledgeEntry

from utils.notification import send_customer_notification

class SalonAIAgent:
    def __init__(self, knowledge_base):
        """Initialize the AI Agent with a knowledge base."""
        self.knowledge_base = knowledge_base
        self.room = None
        self.connection_thread = None
        self.is_running = False
        
        # Basic salon info for the AI
        self.salon_info = {
            "name": "StyleHub Salon",
            "address": "123 Beauty Ave, Fashion City",
            "hours": "Mon-Fri: 9am-7pm, Sat: 10am-6pm, Sun: Closed",
            "services": {
                "haircut": {"price": "$45-$75", "duration": "45 min"},
                "color": {"price": "$85-$150", "duration": "2 hours"},
                "styling": {"price": "$35-$65", "duration": "30 min"},
                "manicure": {"price": "$30-$50", "duration": "45 min"}
            },
            "cancellation_policy": "24 hours notice required to avoid a 50% charge"
        }
    
    def start(self):
        """Start the AI agent in a separate thread."""
        if not self.is_running:
            self.is_running = True
            self.connection_thread = threading.Thread(target=self._run_connection_loop)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            print("AI Agent started and listening for calls...")
    
    def stop(self):
        """Stop the AI agent."""
        self.is_running = False
        if self.connection_thread:
            self.connection_thread.join(timeout=5)
            print("AI Agent stopped.")
    
    def _run_connection_loop(self):
        """Run the connection loop in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_and_listen())
    
    async def _connect_and_listen(self):
        """Connect to LiveKit and listen for calls."""
        api_key = os.getenv('LIVEKIT_API_KEY', 'dev-key')
        api_secret = os.getenv('LIVEKIT_API_SECRET', 'dev-secret')
        url = os.getenv('LIVEKIT_URL', 'ws://localhost:7880')
        
        # For simulation purposes, we'll print connection info instead of actually connecting
        print(f"AI Agent would connect to LiveKit at {url} with API key {api_key}")
        
        while self.is_running:
            # In a real implementation, this would handle actual LiveKit connections
            # For now, we'll just sleep to prevent CPU hogging
            await asyncio.sleep(1)
    
    def process_call(self, session_id, customer_phone, message):
        """Process an incoming call/message from a customer."""
        print(f"Processing call from {customer_phone}: {message}")
        
        # Check if we can answer based on our knowledge
        answer = self.knowledge_base.get_answer(message)
        
        if answer:
            # We know the answer
            return {
                "status": "answered",
                "response": answer,
                "session_id": session_id
            }
        else:
            # We don't know, escalate to supervisor
            return self.request_help(session_id, customer_phone, message)
    
    def request_help(self, session_id, customer_phone, question):
        """Create a help request when the AI doesn't know the answer."""
        print(f"Creating help request for question: {question}")
        
        # Create a new help request in the database
        with current_app.app_context():
            help_request = HelpRequest(
                customer_phone=customer_phone,
                question=question,
                session_id=session_id,
                status='pending',
                created_at=datetime.utcnow()
            )
            db.session.add(help_request)
            db.session.commit()
            
            print(f"Created help request #{help_request.id}")
            
            # Simulate texting the supervisor (in a real app, this would send an actual text)
            # This is handled separately through the notification utility
        
        return {
            "status": "escalated",
            "response": "Let me check with my supervisor and get back to you.",
            "request_id": help_request.id,
            "session_id": session_id
        }
    
    def resolve_help_request(self, request_id, answer):
        """Process a supervisor's response to a help request."""
        with current_app.app_context():
            help_request = HelpRequest.query.get(request_id)
            
            if not help_request:
                return {"status": "error", "message": "Help request not found"}
            
            if help_request.status != 'pending':
                return {"status": "error", "message": f"Help request is already {help_request.status}"}
            
            # Update the help request
            help_request.status = 'resolved'
            help_request.answer = answer
            help_request.resolved_at = datetime.utcnow()
            
            # Update the knowledge base
            knowledge_entry = KnowledgeEntry(
                question=help_request.question,
                answer=answer,
                help_request_id=help_request.id
            )
            db.session.add(knowledge_entry)
            
            # Add to our runtime knowledge base for immediate use
            self.knowledge_base.add_entry(help_request.question, answer)
            
            db.session.commit()
            
            # Follow up with the customer
            self._follow_up_with_customer(help_request)
            
            return {
                "status": "success", 
                "message": f"Help request #{request_id} resolved and knowledge base updated"
            }
    
    def _follow_up_with_customer(self, help_request):
        """Follow up with a customer after their question has been answered."""
        if help_request.customer_phone and help_request.answer:
            # In a real implementation, this would send an actual text
            message = f"Hello! Regarding your question: '{help_request.question}', here's what I found out: {help_request.answer}"
            
            # Simulate sending the message
            send_customer_notification(help_request.customer_phone, message)
            
            # Update follow-up status
            help_request.follow_up_sent = True
            help_request.follow_up_at = datetime.utcnow()
            db.session.commit()
            
            return True
        return False
    
    def simulate_incoming_call(self, phone_number, question):
        """Simulate an incoming call for testing purposes."""
        session_id = f"sim-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return self.process_call(session_id, phone_number, question)