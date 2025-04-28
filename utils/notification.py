import requests
import os
from datetime import datetime

def send_supervisor_notification(message, help_request_id):
    """
    Simulates sending a notification to a supervisor.
    In a real application, this would use Twilio, email or another notification service.
    """
    print(f"[SUPERVISOR NOTIFICATION] Request #{help_request_id}: {message}")
    
    # Log notification to console
    print(f"[{datetime.utcnow()}] Notification sent to supervisor: {message}")
    
    # In a real app, you would have code like this:
    # twilio_client.messages.create(
    #     body=message,
    #     from_=os.getenv('TWILIO_PHONE'),
    #     to=os.getenv('SUPERVISOR_PHONE')
    # )
    
    return True

def send_customer_notification(phone_number, message):
    """
    Simulates sending a notification to a customer.
    In a real application, this would use Twilio or another SMS service.
    """
    print(f"[CUSTOMER NOTIFICATION] To {phone_number}: {message}")
    
    # Log notification to console
    print(f"[{datetime.utcnow()}] Text sent to customer {phone_number}: {message}")
    
    # In a real app, you would have code like this:
    # twilio_client.messages.create(
    #     body=message,
    #     from_=os.getenv('TWILIO_PHONE'),
    #     to=phone_number
    # )
    
    return True