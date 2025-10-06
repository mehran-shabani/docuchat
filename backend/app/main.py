import os

from fastapi import FastAPI
from openai import AsyncOpenAI

# Initialize OpenAI client (optional for development)
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key) if api_key else None

app = FastAPI()


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/v1/chat/demo")
async def demo():
    """
    Demo endpoint for OpenAI chat completion.
    For production with Sonnet 4.5, use model="gpt-4o-sonnet-4.5" and log latency metrics.
    """
    if not client:
        return {"error": "OpenAI API key not configured"}

    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",  # ← Change to gpt-4o-sonnet-4.5 if using Sonnet 4.5
        messages=[{"role": "user", "content": "ping"}],
    )
    return {"reply": res.choices[0].message.content}
