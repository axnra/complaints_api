import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")

    SENTIMENT_API_KEY = os.getenv("SENTIMENT_API_KEY")
    SENTIMENT_API_URL = "https://api.apilayer.com/sentiment/analysis"

    APILAYER_SPAM_API_KEY = os.getenv("APILAYER_SPAMCHECK_API_KEY")
    APILAYER_SPAM_API_URL = "https://api.apilayer.com/spamchecker"

    NINJA_SPAM_API_KEY = os.getenv("NINJA_SPAMCHECK_API_KEY")
    NINJA_SPAM_API_URL = "https://api.api-ninjas.com/v1/spamcheck"

    GEO_API_URL = "http://ip-api.com/json"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    SPAM_THRESHOLD = 2.0
