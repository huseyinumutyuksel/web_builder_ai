import os
import cohere
import logging

logger = logging.getLogger(__name__)

def ask_cohere(prompt: str, purpose: str = "default") -> str:
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        logger.error("COHERE_API_KEY not set")
        return "Error: Cohere API key missing"
    
    co = cohere.Client(api_key)
    try:
        response = co.generate(
            model='command-r', 
            prompt=f"{purpose.upper()}:\n{prompt}",
            max_tokens=300,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        logger.error(f"Cohere API error: {e}", exc_info=True)
        return f"Error: {str(e)}"