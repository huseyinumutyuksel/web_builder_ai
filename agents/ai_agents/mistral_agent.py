import os
import requests
import logging

logger = logging.getLogger(__name__)

def ask_mistral(prompt: str, purpose: str = "default") -> str:
    hf_token = os.getenv("HF_API_TOKEN")
    if not hf_token:
        logger.error("HF_API_TOKEN not set")
        return "Error: Hugging Face API token missing"
    
    headers = {
        "Authorization": f"Bearer {hf_token}"
    }
    payload = {
        "inputs": f"{purpose.upper()}:\n{prompt}",
        "parameters": {"temperature": 0.7}
    }
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # Raises an exception for bad HTTP status codes
        return response.json()[0]['generated_text']
    except requests.exceptions.RequestException as e:
        logger.error(f"Mistral API error: {e}", exc_info=True)
        return f"Error: {str(e)}"
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing Mistral API response: {e}", exc_info=True)
        return "Error: Invalid response from Mistral API"