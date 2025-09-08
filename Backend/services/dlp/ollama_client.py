import os
import json
import asyncio
import aiohttp


class OllamaClientError(RuntimeError):
    """Provider error (timeout/network/format/unavailable)."""
    pass


_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Strict prompt: model must return ONLY a single JSON object with one key.
_PROMPT = (
    'You are a strict classifier. Return ONLY this JSON object: '
    '{"is_baking_recipe": true|false} '
    'Classify if the user message is a baking recipe or clear baking instructions. '
    'Message:\n"""\n{TEXT}\n"""'
)


async def classify_is_baking_recipe(text: str, *, timeout_sec: float = 2.0) -> bool:
    """
    Returns True if the text is a baking recipe/instructions (per Ollama); else False.
    Raises OllamaClientError on timeout/network/format errors.
    """
    prompt_text = _PROMPT.replace("{TEXT}", (text or "")[:6000])
    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": prompt_text,
        "stream": False,
        # Keep it deterministic/fast for classification
        "options": {"temperature": 0}
    }
    url = f"{_OLLAMA_HOST}/api/generate"
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                # Ollama returns { 'response': '<text>', ... }
                result_text = data.get("response", "").strip()
                obj = json.loads(result_text)  # expects {"is_baking_recipe": true/false}
                return bool(obj.get("is_baking_recipe", False))
    except asyncio.TimeoutError as e:
        raise OllamaClientError(f"Ollama timeout ({timeout_sec}s)") from e
    except Exception as e:
        raise OllamaClientError(f"Ollama error: {e}") from e


