from app.db.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE Triage ADD COLUMN created_at TEXT")
    conn.commit()
    print("Column 'created_at' added successfully!")
except Exception as e:
    print(f"Column might already exist or error: {e}")
conn.close()