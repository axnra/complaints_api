from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Complaint(Base):
    """
    SQLAlchemy ORM model representing a customer complaint.

    Attributes:
        id (int): Primary key.
        text (str): Complaint text submitted by the user.
        status (str): Status of the complaint ("open" or "closed").
        timestamp (datetime): Time when the complaint was created.
        sentiment (str): Result of sentiment analysis.
        category (str): Complaint category ("техническая", "оплата", "другое").
    """

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, default="open")
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    sentiment = Column(String, default="unknown")
    category = Column(String, default="другое")
