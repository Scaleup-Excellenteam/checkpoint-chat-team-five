import os
from pathlib import Path
try:
    from dotenv import load_dotenv  # provided via uvicorn[standard]
    # Load root .env (repo root)
    _ROOT = Path(__file__).resolve().parents[2]
    load_dotenv(_ROOT / ".env")
except Exception:
    # If python-dotenv isn't available, env vars must be provided by the shell
    pass


class Settings:
    API_TITLE = "TSPO Chat API"
    API_VERSION = "1.0.0"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
    MAX_MESSAGES_PER_ROOM = int(os.getenv("MAX_MESSAGES_PER_ROOM", "10000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # DLP / Providers
    # Ollama (local LLM)
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # VirusTotal (URL reputation)
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "").strip()
    # Comma-separated keywords to block if found in VT vendor categories
    BLOCKED_URL_CATEGORIES = set(
        c.strip().lower() for c in os.getenv(
            "BLOCKED_URL_CATEGORIES",
            "adult,malware,phishing"
        ).split(",") if c.strip()
    )
    # Quick domain keyword blocklist (substring match on hostname)
    BLOCKED_DOMAIN_KEYWORDS = set(
        k.strip().lower() for k in os.getenv(
            "BLOCKED_DOMAIN_KEYWORDS",
            "porn,xxx,sex"
        ).split(",") if k.strip()
    )
    # Text content keyword blocklist (substring match on message text)
    BLOCKED_TEXT_KEYWORDS = set(
        k.strip().lower() for k in os.getenv(
            "BLOCKED_KEYWORDS",
            ""
        ).split(",") if k.strip()
    )


settings = Settings()
