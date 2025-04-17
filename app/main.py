from fastapi import FastAPI, Depends, HTTPException, Request, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import init_db
from app import schemas, crud
from app.dependencies import (
    get_db,
    get_sentiment_analyzer,
    get_spam_checker,
    get_geo_locator,
    get_category_classifier
)
from app.schemas import ComplaintResponse, StatusFilter, ComplaintCreate, StatusType, ComplaintDetailResponse
from app.external_api.sentiment_analyzer import SentimentAnalyzer
from app.external_api.spam_checker_ninja import SpamChecker
from app.external_api.geo_locator import GeoLocator
from app.external_api.category_classifier import CategoryClassifier
from app.utils.request_utils import extract_client_ip
from app.logger import logger

app = FastAPI()
init_db()


@app.post("/complaints", response_model=ComplaintResponse, summary="Submit a new complaint")
async def create_complaint_endpoint(
    complaint: ComplaintCreate,
    request: Request,
    db: Session = Depends(get_db),
    sentiment_analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer),
    spam_checker: SpamChecker = Depends(get_spam_checker),
    geo_locator: GeoLocator = Depends(get_geo_locator),
    category_classifier: CategoryClassifier = Depends(get_category_classifier)
):
    """
    Submit a new customer complaint for processing and classification.

    Steps:
    - Analyzes sentiment using APILayer.
    - Detects spam.
    - Optionally performs geolocation lookup.
    - Classifies category via LLM (e.g., OpenAI).

    Request Body:
    - text: str – the complaint text

    Returns:
        ComplaintResponse: ID, status (open/closed), sentiment, and category.
    """
    try:
        client_ip = extract_client_ip(request)

        db_complaint = await crud.create_complaint(
            db=db,
            complaint=complaint,
            client_ip=client_ip,
            sentiment_analyzer=sentiment_analyzer,
            spam_checker=spam_checker,
            geo_locator=geo_locator,
            category_classifier=category_classifier
        )

        return ComplaintResponse(
            id=db_complaint.id,
            status=db_complaint.status,
            sentiment=db_complaint.sentiment,
            category=db_complaint.category
        )

    except Exception:
        logger.exception("Unhandled error in create_complaint_endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/complaints", response_model=List[ComplaintDetailResponse], summary="List complaints with optional filters")
def list_complaints(
    status: Optional[StatusFilter] = Query(
        None, description="Filter by complaint status: 'open' or 'closed'"
    ),
    since: Optional[datetime] = Query(
        None, description="Return only complaints created after this datetime (ISO 8601)"
    ),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of complaints, filtered by status and/or creation time.


    Parameters:
    - status: "open" or "closed"
    - since: ISO datetime (only complaints created after this timestamp)

    Returns:
        List[ComplaintDetailResponse]: Matching complaints.
    """
    try:
        complaints = crud.get_complaints(db=db, status=status, since=since)
        return [
            ComplaintDetailResponse(
                id=c.id,
                text=c.text,
                status=c.status,
                sentiment=c.sentiment,
                category=c.category
            ) for c in complaints
        ]
    except Exception:
        logger.exception("Failed to fetch complaints")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.patch("/complaints/{complaint_id}/status", response_model=ComplaintResponse, summary="Update complaint status")
def update_complaint_status(
    complaint_id: int = Path(..., description="ID of the complaint to update"),
    new_status: StatusType = Query(..., description="New status: 'open' or 'closed'"),
    db: Session = Depends(get_db)
):
    """
    Update the status of a complaint to either "open" or "closed".

    Parameters:
    - complaint_id: integer ID of the complaint in the database.
    - new_status: 'open' or 'closed'

    Returns:
        ComplaintResponse: Updated complaint object.

    Raises:
        HTTPException 404: If the complaint is not found.
        HTTPException 500: For internal errors.
    """
    try:
        complaint = crud.update_complaint_status(db=db, complaint_id=complaint_id, new_status=new_status)
        if complaint is None:
            raise HTTPException(status_code=404, detail="Complaint not found")

        return ComplaintResponse(
            id=complaint.id,
            status=complaint.status,
            sentiment=complaint.sentiment,
            category=complaint.category
        )
    except Exception:
        logger.exception("Failed to update complaint status")
        raise HTTPException(status_code=500, detail="Internal server error")
