import os


class Settings:
    API_TITLE = "TSPO Chat API"
    API_VERSION = "1.0.0"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SOCKET_HOST = os.getenv("SOCKET_HOST", "0.0.0.0")
    SOCKET_PORT = int(os.getenv("SOCKET_PORT", "8888"))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
    MAX_MESSAGES_PER_ROOM = int(os.getenv("MAX_MESSAGES_PER_ROOM", "10000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


settings = Settings()
