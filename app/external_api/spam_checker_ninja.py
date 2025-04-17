import httpx

from app.logger import logger
from app.schemas import SpamCheckResult


class SpamCheckServiceError(Exception):
    """Raised when spam check service fails irrecoverably."""


class SpamChecker:
    """
    A client for the API Ninjas Spam Check API.

    This client sends the input text to the external API endpoint and receives
    a spam classification response, including a boolean classification (`is_spam`)
    and a floating-point spam score (`spam_score`).

    The API expects a form-encoded POST request with the target text provided
    in the `text` field. Authentication is handled via the `X-Api-Key` HTTP header.

    API Documentation:
        https://api-ninjas.com/api/spamcheck
    """

    def __init__(self, api_key: str, api_url: str):
        """
        Initializes the SpamChecker client.

        Args:
            api_key (str): API key used for authenticating with API Ninjas.
            api_url (str): Full URL to the spam check endpoint.
        """
        if not api_key:
            raise ValueError("API key for spam check must be provided.")
        self.api_key = api_key
        self.api_url = api_url

    async def check(self, text: str) -> SpamCheckResult:
        """
        Check whether the provided text is considered spam using API Ninjas Spam Checker.

        Args:
            text (str): Text content to evaluate. This can be a plain message or full email body.

        Returns:
            SpamCheckResult: Pydantic model containing:
                - is_spam (bool): Whether the input is considered spam.
                - spam_score (float): Confidence score, typically between 0.0 and 1.0.

        Raises:
            SpamCheckServiceError: If the request fails irrecoverably (e.g., network failure).
        """
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"text": text}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                result = response.json()

                if not isinstance(result, dict):
                    logger.warning(f"Unexpected spamcheck response format: {result}")
                    return SpamCheckResult(is_spam=False, spam_score=0.0)

                return SpamCheckResult(
                    is_spam=result.get("is_spam", False),
                    spam_score=result.get("spam_score", 0.0)
                )

        except httpx.HTTPError:
            logger.exception("HTTP error while checking spam")
            return SpamCheckResult(is_spam=False, spam_score=0.0)

        except Exception as e:
            logger.exception("Unexpected error during spam check")
            raise SpamCheckServiceError from e
