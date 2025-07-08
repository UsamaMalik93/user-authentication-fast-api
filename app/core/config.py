import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings loaded from environment variables
class Settings:
    PROJECT_NAME: str = "FastAPI Auth App"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

# Singleton settings instance
settings = Settings() 