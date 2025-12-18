🏥 MediCare AI
Meta Hackathon 2025 Submission > Empowering patients with instant AI triage via Llama 3 on WhatsApp.

🚀 Overview
MediCare AI is an intelligent Patient Relationship Management (CRM) agent. It bridges the gap between patient symptoms and clinical care by providing instant, safe triage on WhatsApp, allowing Doctor Macaulay to prioritize urgent cases effectively.

✨ Key Features
24/7 Triage: Immediate symptom analysis using Llama 3 8B.

WhatsApp Native: Frictionless access via the world's most popular messaging app.

Doctor-in-the-loop: Automatic escalation of "Red Flag" cases to medical staff.

CRM Integration: Structured triage records saved to a PostgreSQL database.

🛠️ Tech Stack
AI: Meta Llama 3 (via Ollama)

Backend: Python, Flask

Messaging: WhatsApp Business API 

Database: PostgreSQL

Infrastructure: Cloud, Docker

⚙️ Setup & Installation
Clone the repo: git clone https://github.com/your-username/MediConnect-AI.git

Install dependencies: pip install -r requirements.txt

Configure Environment: Create a .env file with your META_ACCESS_TOKEN, META_VERIFY_TOKEN, and DB credentials.

Run Locally: python -m app.main

🔮 Future Roadmap
Multimodal: Voice-to-Triage for better accessibility.

Telemedicine: One-click video consultations within WhatsApp.

RAG: Integration with PubMed for evidence-based medical citations.
