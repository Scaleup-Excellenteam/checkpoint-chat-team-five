import re
import asyncio
from urllib.parse import urlparse
from base64 import urlsafe_b64encode
from typing import List, Dict
import aiohttp
from core.config import settings


class InvalidUrl(Exception):
    """URL failed validation (malicious or blocked category)."""
    pass


_URL_WITH_SCHEME_RX = re.compile(r'(https?://[^\s]+)', re.IGNORECASE)
# Simple bare-domain matcher (captures domains like example.com, www.example.com/path)
_BARE_DOMAIN_RX = re.compile(r'\b((?:www\.)?[a-z0-9.-]+\.[a-z]{2,})(?:/[^\s]*)?', re.IGNORECASE)


def _normalize_url(u: str) -> str:
    # Strip trailing punctuation common in messages
    u = u.rstrip('.,;!?)')
    # Prepend scheme if missing
    if not u.lower().startswith(("http://", "https://")):
        u = "http://" + u
    return u


def extract_urls(text: str) -> List[str]:
    text = text or ""
    urls: List[str] = []
    urls.extend(_URL_WITH_SCHEME_RX.findall(text))
    for m in _BARE_DOMAIN_RX.findall(text):
        urls.append(m)
    # Normalize and de-dup
    normalized: List[str] = []
    seen = set()
    for u in urls:
        nu = _normalize_url(u)
        if nu not in seen:
            seen.add(nu)
            normalized.append(nu)
    return normalized


def is_structurally_valid(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


async def check_virustotal(url: str) -> None:
    """Raise InvalidUrl if VirusTotal flags the URL as malicious/suspicious.

    Strategy:
      1) Check existing verdict via GET /urls/{id} (base64url of URL, no padding)
      2) If missing/pending, submit via POST /urls then poll up to ~3 seconds
    """
    if not settings.VIRUSTOTAL_API_KEY:
        return
    headers = {"x-apikey": settings.VIRUSTOTAL_API_KEY}
    encoded_id = urlsafe_b64encode(url.encode("utf-8")).decode("utf-8").rstrip("=")
    url_obj_api = f"https://www.virustotal.com/api/v3/urls/{encoded_id}"
    submit_api = "https://www.virustotal.com/api/v3/urls"

    async with aiohttp.ClientSession(headers=headers) as s:
        # Try to fetch existing analysis first
        async with s.get(url_obj_api) as r0:
            if r0.status == 200:
                data0 = await r0.json()
                stats = data0["data"]["attributes"].get("last_analysis_stats", {})
                malicious = int(stats.get("malicious", 0))
                suspicious = int(stats.get("suspicious", 0))
                if malicious > 0 or suspicious > 0:
                    raise InvalidUrl("VirusTotal flagged URL as malicious/suspicious")
                # Clean verdict → ok
                return

        # Submit URL for (re)scan
        async with s.post(submit_api, data={"url": url}) as resp:
            resp.raise_for_status()
            data = await resp.json()
            analysis_id = data["data"]["id"]

        analyses_api = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        # Poll briefly for result, then fall back to URL object
        for _ in range(6):  # ~3 seconds @ 0.5s
            async with s.get(analyses_api) as resp2:
                if resp2.status != 200:
                    break
                result = await resp2.json()
                status = result["data"]["attributes"].get("status")
                if status == "completed":
                    stats = result["data"]["attributes"].get("stats", {})
                    malicious = int(stats.get("malicious", 0))
                    suspicious = int(stats.get("suspicious", 0))
                    if malicious > 0 or suspicious > 0:
                        raise InvalidUrl("VirusTotal flagged URL as malicious/suspicious")
                    return
            await asyncio.sleep(0.5)

        # Final check via URL object
        async with s.get(url_obj_api) as r1:
            if r1.status == 200:
                data1 = await r1.json()
                attrs: Dict = data1["data"].get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                malicious = int(stats.get("malicious", 0))
                suspicious = int(stats.get("suspicious", 0))
                if malicious > 0 or suspicious > 0:
                    raise InvalidUrl("VirusTotal flagged URL as malicious/suspicious")
                # Category enforcement (vendor categories)
                cats = []
                cats_map = attrs.get("categories", {}) or {}
                for vendor, cat in cats_map.items():
                    if isinstance(cat, str):
                        cats.append(cat.lower())
                if cats and any(any(k in c for k in settings.BLOCKED_URL_CATEGORIES) for c in cats):
                    raise InvalidUrl(f"Blocked URL category: {','.join(cats)}")
        # Additional domain categories (more reliable for well-known sites)
        try:
            domain = urlparse(url).netloc.lower()
            if domain:
                domains_api = f"https://www.virustotal.com/api/v3/domains/{domain}"
                async with s.get(domains_api) as rd:
                    if rd.status == 200:
                        dd = await rd.json()
                        d_attrs: Dict = dd.get("data", {}).get("attributes", {})
                        d_cats_map = d_attrs.get("categories", {}) or {}
                        d_cats = [str(v).lower() for v in d_cats_map.values() if isinstance(v, str)]
                        if d_cats and any(any(k in c for k in settings.BLOCKED_URL_CATEGORIES) for c in d_cats):
                            raise InvalidUrl(f"Blocked URL category: {','.join(d_cats)}")
        except Exception:
            pass
        # If still no verdict, allow for now (tune to fail-closed if desired)
        return


def _webshrinker_signature(path_with_query: str) -> str:
    raw = path_with_query.encode("utf-8")
    secret = settings.WEBSHRINKER_SECRET_KEY.encode("utf-8")
    digest = hmac.new(secret, raw, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


async def categorize_with_webshrinker(url: str) -> List[str]:
    """Deprecated in favor of VirusTotal; keep for optional use (returns [])."""
    return []


async def validate_urls_in_text(text: str) -> None:
    urls = [u for u in extract_urls(text) if is_structurally_valid(u)]
    if not urls:
        return
    # Quick hostname keyword block (fast path)
    for u in urls:
        host = urlparse(u).netloc.lower()
        if any(k in host for k in settings.BLOCKED_DOMAIN_KEYWORDS):
            raise InvalidUrl("Blocked by hostname keyword policy")
    # VirusTotal reputation check per URL
    for u in urls:
        await check_virustotal(u)
        # Optional category policy using VT's categories (not implemented here)
        # If you want to enforce categories, extend to fetch URL object and compare.