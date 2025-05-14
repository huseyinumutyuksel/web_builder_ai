import os
import requests

HF_TOKEN = os.getenv("HF_API_TOKEN")

def ask_mistral(prompt: str, purpose: str = "default") -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    payload = {
        "inputs": f"{purpose.upper()}:\n{prompt}",
        "parameters": {"temperature": 0.7}
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    return f"Error: {response.text}"
