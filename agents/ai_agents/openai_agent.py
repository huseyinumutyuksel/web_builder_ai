import os
import openai
import logging

logger = logging.getLogger(__name__)

def ask_openai(prompt: str, purpose: str = "default") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        return "Error: OpenAI API key missing"
    
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant for {purpose}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        return f"Error: {str(e)}"