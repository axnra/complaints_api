import httpx

from app.logger import logger
from app.schemas import CategoryResult


class CategoryClassifierError(Exception):
    """
    Raised when the category classification process fails irrecoverably.

    This exception is used to indicate a critical failure, such as a malformed
    response or unexpected runtime error, where fallback behavior is not appropriate.
    """


class CategoryClassifier:
    """
    A classifier for categorizing user complaints using OpenRouter's GPT-4.1 Nano model.

    This client sends a complaint text to the OpenRouter API and expects a single-word
    category in return: "техническая", "оплата", or "другое".

    The classifier is optimized for fast and low-cost inference using the GPT-4.1 Nano model.
    It supports optional proxy usage for environments where OpenRouter is not directly accessible.
    """

    def __init__(self, api_key: str, api_url: str = "https://openrouter.ai/api/v1/chat/completions", proxy: str = None):
        """
        Initialize the classifier with API credentials and optional proxy settings.

        Args:
            api_key (str): The OpenRouter API key.
            api_url (str, optional): The endpoint URL for the OpenRouter chat API. Defaults to GPT-4.1 Nano.
            proxy (str, optional): Optional SOCKS5 proxy URL (e.g., 'socks5://user:pass@host:port') for restricted regions.
        """
        if not api_key:
            raise ValueError("API key for OpenRouter must be provided.")
        self.api_key = api_key
        self.api_url = api_url
        self.proxy = proxy

    async def classify(self, text: str) -> CategoryResult:
        """
        Classify a complaint into one of three predefined categories using GPT-4.1 Nano.

        Args:
            text (str): The complaint text provided by the user.

        Returns:
            CategoryResult: An object containing the predicted category as a lowercase string.

        Raises:
            CategoryClassifierError: If an unexpected exception occurs during classification.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4.1-nano",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Определи категорию жалобы: \"{text}\". "
                        f"Варианты: техническая, оплата, другое. Ответ только одним словом."
                    )
                }
            ],
            "temperature": 0
        }

        try:
            async with httpx.AsyncClient(timeout=10, proxy=self.proxy) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"OpenRouter raw response: {data}")

                category = (
                    data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                        .lower()
                )

                if category not in ("техническая", "оплата", "другое"):
                    logger.warning(f"Unknown or malformed category received from model: {category}")
                    category = "другое"

                return CategoryResult(category=category)

        except httpx.HTTPError:
            logger.exception("HTTP error while fetching category")
            return CategoryResult(category="другое")

        except Exception as e:
            logger.exception("Unexpected error during category classification")
            raise CategoryClassifierError from e
