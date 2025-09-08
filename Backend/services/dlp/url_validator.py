# import re
# from urllib.parse import urlparse
# class InvalidUrl(Exception):
#     """Invalid URL found in message (map to HTTP 422/400 at the API layer)."""
#     pass
# _URL_RX = re.compile(r'(https?://[^\s]+)', re.IGNORECASE)
# def extract_urls(text: str) -> list[str]:
#     return _URL_RX.findall(text or "")
# def is_valid_url(url: str) -> bool:
#     try:
#         p = urlparse(url)
#         return p.scheme in ("http", "https") and bool(p.netloc)
#     except Exception:
#         return False
# def validate_urls_in_text(text: str) -> None:
#     """
#     Raises InvalidUrl if at least one URL is invalid; otherwise silent.
#     """
#     for u in extract_urls(text):
#         if not is_valid_url(u):
#             raise InvalidUrl(f"Invalid URL: {u}")