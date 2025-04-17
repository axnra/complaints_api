from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

StatusType = Literal["open", "closed"]
SentimentType = Literal["positive", "negative", "neutral", "unknown"]
CategoryType = Literal["техническая", "оплата", "другое"]


StatusFilter = StatusType


class ComplaintCreate(BaseModel):
    """
    Incoming data schema for complaint creation.
    Validates that the complaint text is not empty.
    """
    text: str = Field(..., min_length=1, description="The complaint text. Must not be empty.")


class ComplaintResponse(BaseModel):
    """Outgoing schema for complaint response returned to client."""
    id: int
    status: StatusType
    sentiment: SentimentType
    category: CategoryType


class ComplaintDetailResponse(BaseModel):
    """Detailed outgoing schema for complaint response returned to client."""
    id: int
    status: StatusType
    sentiment: SentimentType
    category: CategoryType
    text: str
    timestamp: datetime


class SentimentResult(BaseModel):
    """Represents the result of sentiment analysis."""
    sentiment: SentimentType


class SpamCheckResult(BaseModel):
    """Represents spam check output."""
    is_spam: bool
    spam_score: float


class GeoLocationResult(BaseModel):
    """Contains basic geolocation data based on IP address."""
    country: Optional[str]
    region: Optional[str]
    city: Optional[str]
    ip: str
    status: str  # "success" or "fail"


class CategoryResult(BaseModel):
    """Represents the predicted complaint category."""
    category: CategoryType

