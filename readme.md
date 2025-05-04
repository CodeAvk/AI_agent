# Human-in-the-Loop AI Supervisor

This project implements a human-in-the-loop system for AI agents, where if the AI doesn't know the answer to a question, it will escalate to a human supervisor, follow up with the customer, and update its knowledge base.

## System Overview

The system consists of the following components:

1. **AI Agent**: Simulates an AI receptionist that can answer questions about a salon. If it doesn't know the answer, it escalates to a human supervisor.
2. **Help Request System**: Manages the lifecycle of help requests (pending → resolved/unresolved).
3. **Supervisor Interface**: A web UI for supervisors to view and respond to help requests.
4. **Knowledge Base**: Stores learned answers for future use by the AI agent.
5. **Notification System**: Simulates sending messages to customers and supervisors.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Flask
- LiveKit (for simulated AI agent)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```


### Running the Application

1. Start the application:
   ```
   python app.py
   ```
2. Open a web browser and navigate to `http://localhost:5000`

## Design Decisions

### Help Request Modeling

Help requests are modeled with the following key attributes:
- Customer information (phone number)
- Question content
- Status (pending, resolved, unresolved)
- Answer (if resolved)
- Follow-up tracking

This design allows for:
- Clear tracking of request lifecycle
- Association between questions and answers
- Ability to follow up with customers

### Knowledge Base Structure

The knowledge base is implemented as:
- A runtime dictionary for quick access
- A persistent database table for long-term storage

Knowledge entries contain:
- Original question
- Verified answer
- Reference to the originating help request (if applicable)

### Supervisor Timeout Handling

Timeouts are handled by:
- A background thread that periodically checks for stale requests
- Automatic marking of requests as "unresolved" after 24 hours
- Ability for supervisors to still resolve timed-out requests

### Scaling Considerations

To scale from 10 to 1,000 requests per day:
- Database indexing for faster lookups
- Connection pooling for database access
- Background workers for notifications and follow-ups
- Caching frequently accessed knowledge

### Modularization

The code is organized into logical modules:
- `ai/`: AI agent and knowledge base
- `db/`: Database models and setup
- `web/`: Web interface and routes
- `utils/`: Utility functions like notifications

## Future Improvements

1. Implement Phase 2 with live call transfers
2. Add authentication for supervisors
3. Implement more sophisticated knowledge matching (NLP, embeddings)
4. Add analytics for performance tracking
5. Improve error handling and logging
