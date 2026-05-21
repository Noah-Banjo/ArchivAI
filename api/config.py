import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())

    # 50 MB default upload limit
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024

    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/archivai")
    STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

    # If API_KEY is unset, authentication is disabled (dev/demo mode)
    API_KEY = os.getenv("API_KEY")

    RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "10 per minute")
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
