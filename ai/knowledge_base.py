from db.models import KnowledgeEntry
# from db.
class KnowledgeBase:
    """A simple knowledge base for the AI agent."""
    
    def __init__(self, app=None):
        """Initialize the knowledge base with initial data."""
        self.entries = {}
        
        # Initial knowledge
        self._add_initial_knowledge()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app context to load from database."""
        with app.app_context():
            self._load_from_database()
    
    def _add_initial_knowledge(self):
        """Add initial knowledge about the salon."""
        initial_knowledge = {
            "what are your hours": "We're open Monday to Friday from 9am to 7pm, Saturday from 10am to 6pm, and closed on Sundays.",
            "how much is a haircut": "Haircuts range from $45 to $75 depending on the stylist and complexity.",
            "do you offer color services": "Yes, we offer a full range of color services ranging from $85 to $150 depending on the service.",
            "cancellation policy": "We require 24 hours notice for cancellations to avoid a 50% charge.",
            "where are you located": "We're located at 123 Beauty Ave in Fashion City."
        }
        
        for question, answer in initial_knowledge.items():
            self.entries[question.lower()] = answer
    
    def _load_from_database(self):
        """Load knowledge entries from the database."""
        knowledge_entries = KnowledgeEntry.query.all()
        for entry in knowledge_entries:
            self.entries[entry.question.lower()] = entry.answer
    
    def get_answer(self, question):
        """Get an answer for a question if it exists in the knowledge base."""
        question = question.lower()
        
        # Simple exact match
        if question in self.entries:
            return self.entries[question]
        
        # Simple keyword search
        for key, value in self.entries.items():
            if all(word in question for word in key.split()):
                return value
        
        return None
    
    def add_entry(self, question, answer):
        """Add a new entry to the knowledge base."""
        self.entries[question.lower()] = answer
        return True
    
    def get_all_entries(self):
        """Get all knowledge base entries."""
        return self.entries