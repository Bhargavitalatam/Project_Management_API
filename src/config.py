import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/project_db"
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "dfc3c0ef2ea5d02f37e42d65cd98444458d9299b8214309c6cd7919f91a27e7f"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

settings = Settings()
