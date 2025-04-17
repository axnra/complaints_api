from fastapi import Request


def extract_client_ip(request: Request) -> str:
    """
    Extracts the real client IP address from the request,
    using the 'X-Forwarded-For' header if present, or falling
    back to the direct client IP.

    Args:
        request (Request): FastAPI Request object.

    Returns:
        str: The IP address of the client.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
