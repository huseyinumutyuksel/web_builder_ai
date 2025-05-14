import os
from agents.ai_agents.openai_agent import ask_openai
from agents.ai_agents.cohere_agent import ask_cohere
from agents.ai_agents.mistral_agent import ask_mistral

def generate_content(prompt: str, purpose: str = "default") -> str:
    """
    Belirli bir amaç için seçilen sağlayıcıya göre içerik üretir.
    """
    provider = os.getenv("AI_PROVIDER", "openai").lower()

    if provider == "openai":
        return ask_openai(prompt, purpose)
    elif provider == "cohere":
        return ask_cohere(prompt, purpose)
    elif provider == "mistral":
        return ask_mistral(prompt, purpose)
    else:
        return f"Unsupported AI provider: {provider}"
