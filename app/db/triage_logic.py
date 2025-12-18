import datetime
from app.db.crud import get_or_create_patient, save_triage_record, get_last_triage_record 
from app.utils import llama_api

def run_triage(whatsapp_id: str, patient_input: str) -> dict:
    patient_id = get_or_create_patient(whatsapp_id)
    last_record = get_last_triage_record(patient_id)
    
    appointment_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%A at %I:%M %p")

    # --- PHASE 1: INITIAL GREETING ---
    if not last_record or last_record.get('urgency_level') != 'PENDING':
        response_text = (
            "Hey! 🏥 I'm here. I’ve got my phone on me between rounds.\n\n"
            "*I’m so sorry you're not feeling fine.* To help me figure out how to best help you, "
            "could you quickly answer these for me?\n\n"
            "📍 *WHERE* is the pain or discomfort exactly?\n\n"
            "📊 *SCALE:* On a scale of 1-10, how bad is it?\n\n"
            "🚩 *RED FLAGS:* Are you feeling any dizziness or a very stiff neck?\n\n"
            "--- \n"
            "_I'm checking my messages every few minutes. Please take a sip of water while you type your reply._ 💧"
        )
        
        save_triage_record(patient_id, patient_input, "NURSE_GREETING", {
            "urgency_level": "PENDING", 
            "response_text": response_text
        })
        
        return {"urgency_level": "PENDING", "response_text": response_text}

    # --- PHASE 2: ANALYSIS & DOCTOR ALERT ---
    else:
        system_prompt = f"""
        You are 'Nurse Gemini'. Analyze: {patient_input}
        
        STRICT RULES FOR WHATSAPP LEGIBILITY:
        - Use bolding for keys like *Analysis:* or *Steps:*.
        - Use double line breaks between sections.
        - Use emojis to make it professional but friendly.

        STRUCTURE:
        *ANALYSIS:* (What might be wrong)
        
        *HOME CARE:*
        - (Step 1)
        - (Step 2)
        
        *NEXT STEPS:*
        (If URGENT: Notification alert for Dr. Macaulay. If MILD: Appointment on {appointment_date})
        
        Return JSON ONLY: {{"urgency_level": "URGENT/MILD", "response_text": "..."}}
        """
        
        triage_output = llama_api.generate_triage(system_prompt, patient_input)

        if triage_output.get("urgency_level") == "URGENT":
            print(f"!!! NOTIFYING DOCTOR MACAULAY !!!")

        save_triage_record(patient_id, patient_input, system_prompt, triage_output)
        return triage_output