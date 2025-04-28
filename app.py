import os
from flask import Flask
from db.database import init_db
from db.models import db
from ai.agent import SalonAIAgent
from ai.knowledge_base import KnowledgeBase
from web.routes import web
from dotenv import load_dotenv
import threading
import time

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='web/templates',
                static_folder='web/static')
    
    # Initialize database
    init_db(app)
    
    # Initialize knowledge base and AI agent
    knowledge_base = KnowledgeBase()
    ai_agent = SalonAIAgent(knowledge_base)
    
    # Store the AI agent in the app context for access in routes
    app.ai_agent = ai_agent
    
    # Load knowledge base with app context
    knowledge_base.init_app(app)
    
    # Register blueprints
    app.register_blueprint(web)
    
    # Start the AI agent
    ai_agent.start()
    
    # Start a background thread to periodically check for timeouts
    def check_timeouts_periodically():
        with app.app_context():
            while True:
                # Check for timed out requests every hour
                from web.routes import check_timeouts
                check_timeouts()
                time.sleep(3600)  # Sleep for an hour
    
    timeout_thread = threading.Thread(target=check_timeouts_periodically)
    timeout_thread.daemon = True
    timeout_thread.start()
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)