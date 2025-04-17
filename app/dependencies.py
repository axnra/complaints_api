from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import Settings
from app.external_api.sentiment_analyzer import SentimentAnalyzer
from app.external_api.spam_checker_apilayer import SpamChecker
from app.external_api.geo_locator import GeoLocator
from app.external_api.category_classifier import CategoryClassifier

settings = Settings()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sentiment_analyzer() -> SentimentAnalyzer:
    return SentimentAnalyzer(
        api_key=settings.SENTIMENT_API_KEY,
        api_url=settings.SENTIMENT_API_URL
    )


def get_spam_checker() -> SpamChecker:
    return SpamChecker(
        api_key=settings.APILAYER_SPAM_API_KEY,
        api_url=settings.APILAYER_SPAM_API_URL
    )


def get_geo_locator() -> GeoLocator:
    return GeoLocator(
        base_url=settings.GEO_API_URL
    )


def get_category_classifier() -> CategoryClassifier | None:
    if not settings.OPENAI_API_KEY:
        return None
    return CategoryClassifier(
        api_key=settings.OPENAI_API_KEY,
        api_url=settings.OPENAI_API_URL
    )
