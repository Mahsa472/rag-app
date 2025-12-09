from openai import OpenAI
from config import OPENAI_API_KEY

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def call_llm(prompt: str):
    if not client:
        return "[Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.]"
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Error calling OpenAI API: {str(e)}]"