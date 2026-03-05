"""
llm.py — Mercury 2 dLLM API integration (OpenAI-compatible).

Sends context + question to the Inception Labs Mercury 2 API
and returns the generated answer.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

MERCURY_API_BASE = "https://api.inceptionlabs.ai/v1"
MERCURY_MODEL = "mercury-2"


async def generate_answer(context: str, question: str) -> dict:
    """
    Call Mercury 2 chat/completions endpoint with the retrieved context
    and user question. Returns { "answer": str, "model": str }.
    """
    api_key = os.getenv("MERCURY_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "MERCURY_API_KEY is not set. Add it to your .env file."
        )

    system_prompt = (
        "You are a precise document assistant. Answer the user's question "
        "based ONLY on the provided context. If the context does not contain "
        "enough information, say so clearly. Be concise and accurate."
    )

    payload = {
        "model": MERCURY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"### Context\n{context}\n\n"
                    f"### Question\n{question}"
                ),
            },
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{MERCURY_API_BASE}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()
    answer = data["choices"][0]["message"]["content"]

    return {
        "answer": answer,
        "model": data.get("model", MERCURY_MODEL),
    }
