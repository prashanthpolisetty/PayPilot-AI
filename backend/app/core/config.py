import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Razorpay AI Growth & Agentic Commerce"
    PROJECT_VERSION: str = "1.0.0"

    # Razorpay Credentials
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_TSF2aLs0qkWNQy")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "vZY12hmR64EXQ4RGUsJ639TZ")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_webhook_secret_123")

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./commerce.db")

    # Deterministic Policy Limits (Prices in minor units / paise: INR 100,000 = 10,000,000 paise)
    MAX_TRANSACTION_LIMIT_PAISE: int = int(os.getenv("MAX_TRANSACTION_LIMIT_PAISE", "10000000"))
    MAX_DAILY_SPEND_PAISE: int = int(os.getenv("MAX_DAILY_SPEND_PAISE", "20000000"))
    MAX_QUANTITY_PER_ITEM: int = int(os.getenv("MAX_QUANTITY_PER_ITEM", "5"))
    PAYMENT_REQUIRES_USER_APPROVAL: bool = os.getenv("PAYMENT_REQUIRES_USER_APPROVAL", "true").lower() == "true"
    ALLOWED_CURRENCY: str = "INR"

settings = Settings()
