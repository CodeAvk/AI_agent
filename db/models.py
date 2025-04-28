from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class HelpRequest(db.Model):
    """Model for help requests from AI to human supervisors."""
    id = db.Column(db.Integer, primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    question = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, resolved, unresolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Response from supervisor
    answer = db.Column(db.Text)
    
    # Has the AI followed up with the customer?
    follow_up_sent = db.Column(db.Boolean, default=False)
    follow_up_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"<HelpRequest {self.id}: {self.status}>"

class KnowledgeEntry(db.Model):
    """Model for AI knowledge base entries."""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_request.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    help_request = db.relationship('HelpRequest', backref=db.backref('knowledge_entries', lazy=True))
    
    def __repr__(self):
        return f"<KnowledgeEntry {self.id}: {self.question[:30]}...>"