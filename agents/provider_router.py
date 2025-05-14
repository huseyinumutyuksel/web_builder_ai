import os
import logging
from typing import Dict, Callable
from agents.ai_agents.openai_agent import ask_openai
from agents.ai_agents.cohere_agent import ask_cohere
from agents.ai_agents.mistral_agent import ask_mistral

logger = logging.getLogger(__name__)

# Sağlayıcıları bir sözlükle tanımla
PROVIDERS: Dict[str, Callable[[str, str], str]] = {
    "openai": ask_openai,
    "cohere": ask_cohere,
    "mistral": ask_mistral
}

def generate_content(prompt: str, purpose: str = "default") -> str:
    """
    Belirli bir amaç için seçilen sağlayıcıya göre içerik üretir.
    """
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    logger.info(f"Using AI provider: {provider}")

    if provider not in PROVIDERS:
        error_msg = f"Unsupported AI provider: {provider}"
        logger.error(error_msg)
        return error_msg

    try:
        content = PROVIDERS[provider](prompt, purpose)
        logger.debug(f"Content generated successfully by {provider}")
        return content
    except Exception as e:
        error_msg = f"Error generating content with {provider}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg