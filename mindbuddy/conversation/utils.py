import requests
import os

def get_gpt_response(message):
    groq_api_key = os.getenv("GROQ_API_KEY")
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "user", "content": message}
        ],
        "model": "mixtral-8x7b-32768"  # or the model you're using with Groq
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "Sorry, something went wrong with the AI backend."
