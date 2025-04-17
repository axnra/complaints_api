import httpx

from app.logger import logger
from app.schemas import GeoLocationResult


class GeoLocationServiceError(Exception):
    """Raised when IP geolocation fails irrecoverably."""


class GeoLocator:
    """
    Client for the IP API (http://ip-api.com) to fetch basic geolocation data by IP.
    """

    def __init__(self, base_url: str = "http://ip-api.com/json"):
        self.base_url = base_url

    async def locate(self, ip: str) -> GeoLocationResult:
        """
        Look up IP address and return location info.

        Args:
            ip (str): IP address to be looked up.

        Returns:
            GeoLocationResult: Geolocation info (country, region, city, etc.)

        Raises:
            GeoLocationServiceError: If a fatal error occurs.
        """
        if ip.startswith("127.") or ip == "localhost":
            logger.warning(f"Skipping geo lookup for local IP: {ip}")
            return GeoLocationResult(
                ip=ip, country=None, region=None, city=None, status="skipped"
            )

        url = f"{self.base_url}/{ip}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "success":
                    logger.warning(f"Failed IP lookup for {ip}: {data}")
                    return GeoLocationResult(
                        country=None,
                        region=None,
                        city=None,
                        ip=ip,
                        status="fail"
                    )

                return GeoLocationResult(
                    country=data.get("country"),
                    region=data.get("regionName"),
                    city=data.get("city"),
                    ip=data.get("query", ip),
                    status=data.get("status")
                )

        except httpx.HTTPError:
            logger.exception("HTTP error while fetching geo data")
            return GeoLocationResult(
                country=None,
                region=None,
                city=None,
                ip=ip,
                status="fail"
            )

        except Exception as e:
            logger.exception("Unexpected error during IP geolocation")
            raise GeoLocationServiceError from e
