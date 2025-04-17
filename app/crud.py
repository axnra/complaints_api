from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import Complaint
from app.schemas import ComplaintCreate
from app.external_api.sentiment_analyzer import SentimentAnalyzer
from app.external_api.spam_checker_apilayer import SpamChecker
from app.external_api.geo_locator import GeoLocator
from app.external_api.category_classifier import CategoryClassifier
from app.schemas import SentimentResult, SpamCheckResult, StatusType
from app.logger import logger
from app.config import Settings


async def create_complaint(
    db: Session,
    complaint: ComplaintCreate,
    client_ip: str,
    sentiment_analyzer: SentimentAnalyzer,
    spam_checker: SpamChecker | None,
    geo_locator: GeoLocator,
    category_classifier: CategoryClassifier
) -> Complaint:
    """
    Creates a new complaint record in the database, enriched with metadata
    obtained from external services.

    This function performs a multistep enrichment workflow:
        1. Analyzes sentiment of the complaint using the APILayer Sentiment API.
        2. Detects spam via the APILayer Spam Checker (marks as closed if score ≥ threshold).
        3. Resolves geolocation of the client's IP (skipped if IP is local).
        4. Persists the complaint in the database with initial metadata.
        5. Classifies the complaint category (техническая, оплата, другое) using OpenAI GPT-3.5 Turbo.
           Updates the record with the determined category post-creation.

    In case of external API failures, safe fallbacks are used, and the process continues.
    All key operations are logged for traceability.

    Args:
        db (Session): SQLAlchemy session for DB interaction.
        complaint (ComplaintCreate): Complaint payload from the user.
        client_ip (str): IP address of the requester, used for geo lookup.
        sentiment_analyzer (SentimentAnalyzer): Sentiment analysis service client.
        spam_checker (SpamChecker): Spam detection service client.
        geo_locator (GeoLocator): IP geolocation client.
        category_classifier (CategoryClassifier): GPT-based classifier for complaint categories.

    Returns:
        Complaint: The fully initialized and saved complaint object from the database.
    """

    logger.info("Starting complaint creation...")

    # Sentiment analysis
    try:
        sentiment = await sentiment_analyzer.analyze(complaint.text)
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        sentiment = SentimentResult(sentiment="unknown")
    logger.debug(f"Sentiment: {sentiment.sentiment}")

    # Spam detection
    # try:
    #     spam_result = await spam_checker.check(complaint.text, threshold=Settings.SPAM_THRESHOLD)
    # except Exception as e:
    #     logger.warning(f"Spam check failed: {e}")
    #     spam_result = SpamCheckResult(is_spam=False, spam_score=0.0)
    # logger.debug(f"Spam score: {spam_result.spam_score}, Is spam: {spam_result.is_spam}")
    #
    # # Geolocation (optional)
    # try:
    #     geo_result = await geo_locator.locate(client_ip)
    #     logger.debug(f"Geo result for IP {client_ip}: {geo_result}")
    # except Exception as e:
    #     logger.warning(f"Geolocation failed: {e}")

    # Initial complaint creation
    db_complaint = Complaint(
        text=complaint.text,
        sentiment=sentiment.sentiment,
        status="open",
        category="другое"
    )

    try:
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        logger.info(f"Complaint created in DB with ID {db_complaint.id}")
    except Exception as e:
        logger.exception("Database error while creating complaint")
        raise

    # Category classification
    if category_classifier:
        try:
            category_result = await category_classifier.classify(complaint.text)
            db_complaint.category = category_result.category
            db.commit()
            logger.info(f"Category updated to '{category_result.category}' for complaint ID {db_complaint.id}")
        except Exception as e:
            logger.warning(f"Category classification failed for complaint ID {db_complaint.id}: {e}")

    return db_complaint


def get_complaints(
    db: Session,
    status: Optional[str] = None,
    since: Optional[datetime] = None
) -> List[type(Complaint)]:
    """
    Retrieve complaints from the database filtered by status and/or timestamp.

    Args:
        db (Session): SQLAlchemy session.
        status (str, optional): Filter by complaint status ("open" or "closed").
        since (datetime, optional): Filter by creation timestamp (greater than or equal).

    Returns:
        List[Complaint]: Filtered list of complaints.
    """
    query = db.query(Complaint)

    if status:
        query = query.filter(Complaint.status == status)

    if since:
        query = query.filter(Complaint.timestamp >= since)

    return query.order_by(Complaint.timestamp.desc()).all()


def update_complaint_status(
    db: Session,
    complaint_id: int,
    new_status: StatusType
) -> Complaint:
    """
    Updates the status of an existing complaint.

    Args:
        db (Session): SQLAlchemy database session.
        complaint_id (int): ID of the complaint to update.
        new_status (str): New status to set ("open" or "closed").

    Returns:
        Complaint: The updated complaint object.

    Raises:
        ValueError: If complaint not found.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise ValueError(f"Complaint with ID {complaint_id} not found")

    complaint.status = new_status
    db.commit()
    db.refresh(complaint)
    return complaint
