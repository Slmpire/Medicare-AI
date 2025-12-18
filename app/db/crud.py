from app.db.database import get_db_connection
import datetime

def get_or_create_patient(whatsapp_id: str, name: str = None) -> int:
    """Checks if a patient exists by whatsapp_id; creates them if not found."""
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM Patient WHERE whatsapp_id = ?", (whatsapp_id,))
    patient = cursor.fetchone()
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if patient:
        patient_id = patient['id']
        cursor.execute("UPDATE Patient SET last_message_ts = ? WHERE id = ?", (now_str, patient_id))
    else:
        cursor.execute("""
            INSERT INTO Patient (whatsapp_id, name, last_message_ts) 
            VALUES (?, ?, ?)
        """, (whatsapp_id, name if name else "WhatsApp Patient", now_str))
        patient_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return patient_id

def get_last_triage_record(patient_id: int):
    """
    Retrieves the most recent triage record for a patient.
    This allows the logic to see if we are in the middle of a conversation.
    """
    conn = get_db_connection()
    # This allows us to access data like record['urgency_level']
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM Triage 
        WHERE patient_id = ? 
        ORDER BY created_at DESC LIMIT 1
    """, (patient_id,))
    
    record = cursor.fetchone()
    conn.close()
    return record

def save_triage_record(patient_id: int, symptoms: str, llama_input: str, triage_data: dict) -> int:
    """Saves the result of an AI triage interaction into the Triage table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO Triage (patient_id, symptoms, llama_input, urgency_level, agent_response, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id, 
        symptoms, 
        llama_input, 
        triage_data.get('urgency_level', 'MILD'), 
        triage_data.get('response_text', ''),
        now_str
    ))
    
    triage_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return triage_id