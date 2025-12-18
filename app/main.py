import os
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from app.triage.triage_logic import run_triage
from app.utils.whatsapp_api import send_whatsapp_message

load_dotenv()
app = Flask(__name__)

# --- NEW: Deduplication Tracker ---
# This stores message IDs for the current session to prevent duplicate replies.
processed_messages = set()

def process_async_triage(sender_id, message_body, message_id):
    try:
        # Run your LLM logic
        triage_result = run_triage(sender_id, message_body)
        response_text = triage_result.get('response_text')
        
        # Send the reply
        send_whatsapp_message(sender_id, response_text)
        print(f"✅ Successfully sent reply for Message ID: {message_id}")
    except Exception as e:
        print(f"❌ Async error: {e}")
    # Optional: You could remove from set after some time, 
    # but for a 30s demo, keeping it in the set is fine.

@app.route('/webhook', methods=['POST'])
def handle_whatsapp_webhook():
    try:
        data = request.get_json(force=True, silent=True) or {}

        # 1. Extract message details AND the unique Message ID
        sender_id = None
        message_body = None
        message_id = None # Meta provides a unique 'id' for every message
        
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    if messages:
                        msg = messages[0]
                        sender_id = msg.get('from')
                        message_id = msg.get('id') # Extract the unique ID
                        message_body = msg.get('text', {}).get('body')

        # 2. THE FIX: Check if we have already seen this ID
        if message_id in processed_messages:
            print(f"♻️ Duplicate detected (ID: {message_id}). Skipping.")
            return "Duplicate", 200

        if sender_id and message_body and message_id:
            # Mark as processed immediately
            processed_messages.add(message_id)
            
            print(f"📩 New message: '{message_body}'. ID: {message_id}")
            
            # Start background thread
            thread = threading.Thread(target=process_async_triage, args=(sender_id, message_body, message_id))
            thread.start()

            return "OK", 200

        return "No message found", 200

    except Exception as e:
        print(f"⚠️ Webhook error: {e}")
        return "OK", 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    if request.args.get('hub.verify_token') == os.getenv('META_VERIFY_TOKEN'):
        return request.args.get('hub.challenge'), 200
    return "Failed", 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)