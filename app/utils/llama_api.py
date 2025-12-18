import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables for configuration
load_dotenv()
LLAMA_ENDPOINT = os.getenv("LLAMA_ENDPOINT", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL_8B", "llama3:8b") 

def generate_triage(system_prompt: str, user_input: str) -> dict:
    """
    Sends the combined prompt and user input to the local Ollama API 
    and attempts to parse the structured JSON response.
    """
    
    # Use the full prompt template from the triage_prompt.txt file, 
    # substituting the patient's symptoms into the placeholder.
    full_prompt = system_prompt.replace("{patient_symptoms}", user_input)
    
    # The data payload required by the Ollama /api/generate endpoint
    data = {
        "model": LLAMA_MODEL,
        "prompt": full_prompt,
        "format": "json",  # CRITICAL: Forces Llama to output valid JSON
        "stream": False,
        "options": {
            "temperature": 0.2, # Low temperature for reliable, non-creative classification
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        # 1. Send the request to Ollama
        response = requests.post(f"{LLAMA_ENDPOINT}/api/generate", 
                                 headers=headers, 
                                 data=json.dumps(data), 
                                 timeout=90) # Add a timeout for safety
        
        # Raise an exception for HTTP error codes (4xx, 5xx)
        response.raise_for_status() 
        
        # 2. Extract the LLM's response text
        result = response.json()
        llama_text = result.get('response', '').strip()
        
        # 3. Clean and parse the JSON block
        if llama_text.startswith('{') and llama_text.endswith('}'):
             # Direct JSON output
            json_data = llama_text
        elif '```json' in llama_text:
             # Extract the JSON block if Llama wrapped it in markdown
            json_block = llama_text.split('```json')[1].split('```')[0].strip()
            json_data = json_block
        else:
             # Handle cases where Llama returns text but not perfect JSON
             raise json.JSONDecodeError(f"LLM output was not in expected JSON format: {llama_text}", llama_text, 0)
        
        # Return the parsed dictionary
        return json.loads(json_data)

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not communicate with Ollama API: {e}")
        # Default safe response for technical failure
        return {"urgency_level": "NON-URGENT", 
                "response_text": "We are experiencing a severe technical difficulty and cannot process your symptoms right now. Please call the clinic directly.", 
                "detected_language": "en"}

    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to decode JSON from Ollama. Prompt/Model likely failed: {e}")
        # Default safe response for LLM parsing failure
        return {"urgency_level": "MODERATE", 
                "response_text": "We could not categorize your message accurately. Please try rephrasing your symptoms or contact the clinic immediately if your condition is serious.", 
                "detected_language": "en"}