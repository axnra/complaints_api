import httpx

from app.logger import logger
from app.schemas import CategoryResult


class CategoryClassifierError(Exception):
    """Raised when category classification fails irrecoverably."""


class CategoryClassifier:
    """
    A client for the OpenAI GPT-3.5 Turbo API for category classification.

    This client sends user complaints to OpenAI's ChatCompletion endpoint and receives
    a single-word classification response: one of "техническая", "оплата", or "другое".

    The model is instructed via prompt to return only one of the predefined categories.

    If the service is unavailable, produces an unexpected response, or throws an error,
    the system logs the issue and gracefully falls back to returning "другое".

    API Documentation:
        https://platform.openai.com/docs/guides/chat/introduction
    """

    def __init__(self, api_key: str, api_url: str = "https://api.openai.com/v1/chat/completions"):
        if not api_key:
            raise ValueError("API key for OpenAI must be provided.")
        self.api_key = api_key
        self.api_url = api_url

    async def classify(self, text: str) -> CategoryResult:
        """
        Classify a user complaint into one of three categories using GPT-3.5 Turbo.

        Args:
            text (str): The complaint text to analyze.

        Returns:
            CategoryResult: Pydantic model with the category string.
                            One of: "техническая", "оплата", "другое".

        Raises:
            CategoryClassifierError: If an unexpected error occurs during the request.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {
                "role": "user",
                "content": (
                    f"Определи категорию жалобы: \"{text}\". "
                    f"Варианты: техническая, оплата, другое. Ответ только одним словом."
                )
            }
        ]

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                category = (
                    data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                        .lower()
                )

                if category not in ("техническая", "оплата", "другое"):
                    logger.warning(f"Unknown or malformed category received from GPT: {category}")
                    category = "другое"

                return CategoryResult(category=category)

        except httpx.HTTPError:
            logger.exception("HTTP error while fetching category")
            return CategoryResult(category="другое")

        except Exception as e:
            logger.exception("Unexpected error during category classification")
            raise CategoryClassifierError from e
