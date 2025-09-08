import os
import json
import asyncio
import aiohttp
class GeminiClientError(RuntimeError):
    """Provider error (timeout/network/format/missing key)."""
    pass
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
# Strict prompt: model must return ONLY a single JSON object with one key.
_PROMPT = (
    'You are a strict classifier. Return ONLY this JSON object: '
    '{"is_baking_recipe": true|false} '
    'Classify if the user message is a baking recipe or clear baking instructions. '
    'Message:\n\"\"\"\n{TEXT}\n\"\"\"'
)
async def classify_is_baking_recipe(text: str, *, timeout_sec: float = 2.5) -> bool:
    """
    Returns True if the text is a baking recipe/instructions (per Gemini); else False.
    Raises GeminiClientError on timeout/network/format errors.
    """
    if not _GEMINI_API_KEY:
        raise GeminiClientError("GEMINI_API_KEY is missing")
    prompt_text = _PROMPT.replace("{TEXT}", (text or "")[:6000])
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    params = {"key": _GEMINI_API_KEY}
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(_GEMINI_URL, params=params, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                obj = json.loads(result_text)  # expects {"is_baking_recipe": true/false}
                return bool(obj.get("is_baking_recipe", False))
    except asyncio.TimeoutError as e:
        raise GeminiClientError(f"Gemini timeout ({timeout_sec}s)") from e
    except Exception as e:
        raise GeminiClientError(f"Gemini error: {e}") from e