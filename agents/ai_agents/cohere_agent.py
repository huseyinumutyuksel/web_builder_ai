import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def ask_cohere(prompt: str, purpose: str = "default") -> str:
    response = co.generate(
        model='command-r', 
        prompt=f"{purpose.upper()}:\n{prompt}",
        max_tokens=300,
        temperature=0.7
    )
    return response.generations[0].text.strip()
