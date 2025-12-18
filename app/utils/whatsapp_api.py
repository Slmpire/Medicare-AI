import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Variables from your .env file
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
SENDER_PHONE_ID = os.getenv('META_SENDER_ID')

def send_whatsapp_message(to_number: str, body_text: str):
    """Sends a text message using the Meta/Facebook WhatsApp Business API.
    
    Ensures the recipient number is clean and the request uses the correct Meta headers.
    """
    
    if not ACCESS_TOKEN or not SENDER_PHONE_ID:
        print("ERROR: Meta API credentials missing from .env. Cannot send message.")
        return False

    # CRITICAL FIX: Clean the recipient number to ensure it only contains digits 
    # (Meta requires the full international code without '+' or spaces)
    clean_to_number = ''.join(filter(str.isdigit, to_number))

    # The Meta API endpoint for sending messages
    META_API_URL = f"https://graph.facebook.com/v18.0/{SENDER_PHONE_ID}/messages"

    # Data payload required by the Meta API (JSON format)
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_to_number, # Use the cleaned number for strict compliance
        "type": "text",
        "text": {
            "body": body_text
        }
    }

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(META_API_URL, 
                                 headers=headers, 
                                 data=json.dumps(payload))
        
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        
        if response.status_code in [200, 201]:
            print(f"Successfully sent Meta WhatsApp message to {clean_to_number}")
            return True
        else:
            # This line should ideally not be reached if raise_for_status() works, 
            # but is kept for detailed logging of unexpected non-error statuses.
            print(f"Failed to send message. Status: {response.status_code}. Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        # Log the specific request error for debugging (e.g., 400 Bad Request)
        print(f"Error sending Meta WhatsApp message via API: {e}")
        
        # Log the actual response text from the Meta API to get the specific reason for 400
        if e.response is not None:
             print(f"Meta API Error Details: {e.response.text}")
        
        return False