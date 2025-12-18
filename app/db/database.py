import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables (like the DB path) from the .env file
load_dotenv() 

# 1. Determine the Database Path
# We read the path from the .env file and strip the SQLite prefix.
# Example: "sqlite:///./db/mediconnect.db" -> "db/mediconnect.db"
DB_URL = os.getenv("DATABASE_URL")
if DB_URL.startswith("sqlite:///./"):
    DB_PATH = DB_URL.replace("sqlite:///./", "")
else:
    # Fallback path if .env is missing or incorrect
    DB_PATH = "db/mediconnect.db" 


def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    # This line connects to the file. If the file doesn't exist, SQLite creates it.
    conn = sqlite3.connect(DB_PATH)
    # Allows us to access columns by their name (e.g., row['id']) instead of index
    conn.row_factory = sqlite3.Row 
    return conn

def initialize_db():
    """Creates all necessary tables if they do not already exist."""
    print("--- Initializing Database Schema ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Patient Table: Stores contact info and language preference
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_id TEXT UNIQUE NOT NULL, -- The patient's WhatsApp phone number (Crucial unique identifier)
            name TEXT,
            language TEXT DEFAULT 'en',
            last_message_ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 2. Triage Table: Stores all symptom reports and AI classifications (Day 1 Key Deliverable)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Triage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL,
            llama_input TEXT,
            urgency_level TEXT NOT NULL, -- EMERGENCY, URGENT, MODERATE, NON-URGENT
            agent_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES Patient (id)
        );
    """)

    # 3. Appointment Table: Stores booking details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Appointment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            clinic_service TEXT NOT NULL,
            datetime DATETIME NOT NULL,
            status TEXT DEFAULT 'Scheduled', -- Scheduled, Canceled, Completed, No-Show
            is_reminder_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES Patient (id)
        );
    """)

    # 4. Feedback Table: Stores post-visit patient reviews
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_id INTEGER,
            rating INTEGER, -- 1 to 5
            sentiment TEXT, -- Positive, Neutral, Negative
            raw_feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES Patient (id),
            FOREIGN KEY (appointment_id) REFERENCES Appointment (id)
        );
    """)

    # Commit the changes (create the tables) and close the connection
    conn.commit()
    conn.close()
    print("--- Database Schema Initialization Complete ---")

# Run this function immediately so the db file is created.
initialize_db()