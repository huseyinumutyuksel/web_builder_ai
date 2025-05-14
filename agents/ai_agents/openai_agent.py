import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt: str, purpose: str = "default") -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant for {purpose}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message["content"]
