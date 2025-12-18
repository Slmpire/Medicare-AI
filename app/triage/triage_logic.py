import os
from datetime import datetime, timedelta
from app.db.crud import get_or_create_patient, save_triage_record, get_last_triage_record 
from app.utils import llama_api

def run_triage(whatsapp_id: str, patient_input: str) -> dict:
    """
    State-aware triage: Checks if the patient is greeting us or answering questions.
    """
    # 1. Get Patient and check for recent history (last 24 hours)
    patient_id = get_or_create_patient(whatsapp_id, name="WhatsApp Patient")
    last_record = get_last_triage_record(patient_id) # You need a function to fetch the last row
    
    appointment_date = (datetime.now() + timedelta(days=1)).strftime("%A at %I:%M %p")

    # --- SCENARIO A: THIS IS A NEW CONVERSATION (GREETING) ---
    # If there is no record, or the last record was solved/old, we start fresh.
    if not last_record:
        response_text = (
            "Hey! 🏥 I'm here. I’ve got my phone on me between rounds.\n\n"
            "I’m so sorry you're not feeling fine. To better respond and help you feel better, "
            "can you answer these 3 quick questions for me?\n"
            "1. Where is the pain or discomfort exactly?\n"
            "2. On a scale of 1-10, how bad is the pain?\n"
            "3. Do you have a fever, dizziness, or a very stiff neck?"
        )
        
        # Save an 'initial' record so the next message is treated as a follow-up
        save_triage_record(patient_id, patient_input, "NURSE_GREETING", {"urgency_level": "PENDING"})
        
        return {"urgency_level": "PENDING", "response_text": response_text}

    # --- SCENARIO B: THIS IS A FOLLOW-UP (ANALYSIS) ---
    # The patient is now providing the answers to the questions above.
    else:
        system_prompt = f"""
        You are 'Nurse Gemini'. Analyze these patient answers: {patient_input}
        
        URGENCY RULES:
        - URGENT: If they report 8-10 pain, stiff neck, confusion, or inability to breathe.
        - MILD: If symptoms are manageable (low pain, no red flags).

        STRICT RESPONSE STRUCTURE:
        1. ANALYSIS: "Based on what you told me, it sounds like [Possible Cause]."
        2. SOLUTIONS: Give 3 safe home-care steps.
        3. CLOSING:
            - IF URGENT: "🚨 URGENT: Doctor Macaulay has been notified immediately. Please go to the ER or call emergency services now."
            - IF MILD: "Since this seems manageable, I’ve tentatively fixed an appointment for you on {appointment_date}. Doctor Macaulay will review your record then. Get some rest and feel better! ✨"
        
        Return JSON ONLY: {{"urgency_level": "URGENT/MILD", "response_text": "..."}}
        """
        
        triage_output = llama_api.generate_triage(system_prompt, patient_input)

        # Trigger real-time alert if URGENT
        if triage_output.get("urgency_level") == "URGENT":
            # notify_doctor_macaulay(patient_id, patient_input)
            print("ALERT: Doctor Macaulay notified.")

        # Save the final analysis and clear the state (or mark as handled)
        save_triage_record(patient_id, patient_input, system_prompt, triage_output)
        
        return triage_output