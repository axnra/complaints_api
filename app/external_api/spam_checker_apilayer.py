import httpx

from app.logger import logger
from app.schemas import SpamCheckResult


class SpamCheckServiceError(Exception):
    """Raised when spam check service fails irrecoverably."""


class SpamChecker:
    """
    A client for the APILayer Spam Check API.

    This client sends the input text to the external API endpoint and receives
    a spam classification response, including a boolean classification (`is_spam`)
    and a floating-point spam score (`score`).

    The `threshold` parameter is passed as a query parameter and determines the
    minimum score above which the content is considered spam.

    The API expects a JSON POST request with the `text` field in the body.
    Authentication is handled via the `apikey` HTTP header.

    API Documentation:
        https://apilayer.com/marketplace/spamchecker-api#documentation-tab
    """

    def __init__(self, api_key: str, api_url: str):
        """
        Initializes the SpamChecker client.

        Args:
            api_key (str): API key used for authenticating with APILayer.
            api_url (str): Base URL of the spam checker API.
        """
        if not api_key:
            raise ValueError("API key for spam check must be provided.")
        self.api_key = api_key
        self.api_url = api_url

    async def check(self, text: str, threshold: float = 5.0) -> SpamCheckResult:
        """
        Check whether the provided text is considered spam using APILayer Spam Checker.

        Args:
            text (str): Text content to evaluate.
            threshold (float): Score threshold to classify the content as spam (default: 5.0).
                               This is passed as a query parameter to the API.

        Returns:
            SpamCheckResult: Pydantic model with is_spam (bool) and spam_score (float).

        Raises:
            SpamCheckServiceError: If an unexpected error occurs during the request.
        """
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        params = {"threshold": threshold}
        json_data = {"text": text}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    params=params,
                    json=json_data
                )
                response.raise_for_status()
                result = response.json()

                if not isinstance(result, dict):
                    logger.warning(f"Unexpected spamcheck response format: {result}")
                    return SpamCheckResult(is_spam=False, spam_score=0.0)

                return SpamCheckResult(
                    is_spam=result.get("is_spam", False),
                    spam_score=result.get("score", 0.0)
                )

        except httpx.HTTPError:
            logger.exception("HTTP error while checking spam")
            return SpamCheckResult(is_spam=False, spam_score=0.0)

        except Exception as e:
            logger.exception("Unexpected error during spam check")
            raise SpamCheckServiceError from e
