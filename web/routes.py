from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
from db.models import db, HelpRequest, KnowledgeEntry
from utils.notification import send_supervisor_notification

web = Blueprint('web', __name__)

@web.route('/')
def index():
    """Dashboard showing system overview."""
    pending_count = HelpRequest.query.filter_by(status='pending').count()
    resolved_count = HelpRequest.query.filter_by(status='resolved').count()
    unresolved_count = HelpRequest.query.filter_by(status='unresolved').count()
    
    # Get recent requests
    recent_requests = HelpRequest.query.order_by(HelpRequest.created_at.desc()).limit(5).all()
    
    # Get knowledge base entry count
    kb_count = KnowledgeEntry.query.count()
    
    return render_template('dashboard.html', 
                           pending_count=pending_count,
                           resolved_count=resolved_count,
                           unresolved_count=unresolved_count,
                           recent_requests=recent_requests,
                           kb_count=kb_count)

@web.route('/requests')
def view_requests():
    """View and manage help requests."""
    status = request.args.get('status', 'pending')
    
    # Query requests by status
    if status == 'all':
        requests = HelpRequest.query.order_by(HelpRequest.created_at.desc()).all()
    else:
        requests = HelpRequest.query.filter_by(status=status).order_by(HelpRequest.created_at.desc()).all()
    
    return render_template('requests.html', requests=requests, current_status=status)

@web.route('/knowledge')
def view_knowledge():
    """View and manage knowledge base entries."""
    entries = KnowledgeEntry.query.order_by(KnowledgeEntry.created_at.desc()).all()
    return render_template('knowledge.html', entries=entries)

@web.route('/api/requests/<int:request_id>/resolve', methods=['POST'])
def resolve_request(request_id):
    """API endpoint to resolve a help request."""
    answer = request.json.get('answer')
    
    if not answer:
        return jsonify({'status': 'error', 'message': 'Answer is required'}), 400
    
    help_request = HelpRequest.query.get_or_404(request_id)
    
    # If already resolved or unresolved, return error
    if help_request.status != 'pending':
        return jsonify({'status': 'error', 'message': f'Request is already {help_request.status}'}), 400
    
    # Use the AI agent to resolve the request, which will:
    # 1. Update the help request status
    # 2. Add to knowledge base
    # 3. Follow up with customer
    result = current_app.ai_agent.resolve_help_request(request_id, answer)
    
    return jsonify(result)

@web.route('/api/simulate/call', methods=['POST'])
def simulate_call():
    """API endpoint to simulate an incoming call for testing."""
    phone = request.json.get('phone', '+15551234567')
    question = request.json.get('question')
    
    if not question:
        return jsonify({'status': 'error', 'message': 'Question is required'}), 400
    
    # Process the simulated call through the AI agent
    result = current_app.ai_agent.simulate_incoming_call(phone, question)
    
    # If escalated, send notification to supervisor
    if result.get('status') == 'escalated':
        message = f"Hey, I need help answering: '{question}' from customer {phone}"
        send_supervisor_notification(message, result.get('request_id'))
    
    return jsonify(result)

@web.route('/api/check-timeouts')
def check_timeouts():
    """Check for help requests that have timed out and mark them unresolved."""
    # Define timeout period (e.g., 24 hours)
    timeout_period = datetime.utcnow() - timedelta(hours=24)
    
    # Find pending requests older than the timeout
    timed_out_requests = HelpRequest.query.filter(
        HelpRequest.status == 'pending',
        HelpRequest.created_at < timeout_period
    ).all()
    
    # Mark them as unresolved
    for request in timed_out_requests:
        request.status = 'unresolved'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Marked {len(timed_out_requests)} requests as unresolved due to timeout'
    })