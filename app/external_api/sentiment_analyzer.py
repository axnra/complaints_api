import httpx

from app.logger import logger
from app.schemas import SentimentResult


class SentimentServiceError(Exception):
    """Raised when sentiment analysis fails irrecoverably."""


class SentimentAnalyzer:
    """
    A client for the APILayer Sentiment Analysis API.

    This client sends the input text to the external API endpoint and receives
    a sentiment classification response, including one of the values:
    "positive", "negative", or "neutral".

    If the service is unavailable or returns an invalid response, the sentiment
    is safely downgraded to "unknown" and logged as a warning.

    The API expects a JSON POST request with a `text` field in the request body.
    Authentication is handled via the `apikey` HTTP header.

    API Documentation:
        https://apilayer.com/marketplace/sentiment-analysis-api
    """

    def __init__(self, api_key: str, api_url: str):
        if not api_key:
            raise ValueError("API key for sentiment analysis must be provided.")
        self.api_key = api_key
        self.api_url = api_url

    async def analyze(self, text: str) -> SentimentResult:
        """
        Analyze the sentiment of a given text using APILayer Sentiment Analysis API.

        Args:
            text (str): The input text to analyze.

        Returns:
            SentimentResult: Pydantic model containing the detected sentiment.
                             Possible values: "positive", "negative", "neutral", or "unknown".

        Raises:
            SentimentServiceError: If an unexpected error occurs during the request,
                                   such as a timeout or malformed response.
        """
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }

        payload = {"text": text}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                sentiment = data.get("sentiment", "unknown")

                if sentiment not in ("positive", "negative", "neutral"):
                    logger.warning(f"Unknown sentiment value received: {sentiment}")
                    sentiment = "unknown"

                return SentimentResult(sentiment=sentiment)

        except httpx.HTTPError:
            logger.exception("HTTP error while fetching sentiment")
            return SentimentResult(sentiment="unknown")

        except Exception as e:
            logger.exception("Unexpected error during sentiment analysis")
            raise SentimentServiceError from e
