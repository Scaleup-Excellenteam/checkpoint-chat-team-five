import json
from pathlib import Path
from threading import RLock
from typing import Set, List
import ipaddress
from datetime import datetime
import re


class InvalidIP(Exception):
    """Raised when a client IP is blocked by policy or blocklists."""
    pass


# Paths: repo_root/Data
_repo_root = Path(__file__).resolve().parents[3]
_data_dir = _repo_root / "Data"
_data_dir.mkdir(parents=True, exist_ok=True)
_blocked_ips_path = _data_dir / "blocked_ips.json"
_blocked_cidrs_path = _data_dir / "blocked_ip_cidrs.json"


_cache_lock: RLock = RLock()
_blocked_ips: Set[str] = set()
_blocked_networks: List[ipaddress._BaseNetwork] = []
_last_mtime_ips: float = 0.0
_last_mtime_cidrs: float = 0.0


def _read_json_list(path: Path) -> List[str]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [str(x).strip() for x in data if x]
    except Exception:
        pass
    return []


def _write_json_list(path: Path, items: List[str]) -> None:
    try:
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # best-effort only
        pass


def _load_blocklists() -> None:
    global _blocked_ips, _blocked_networks, _last_mtime_ips, _last_mtime_cidrs
    with _cache_lock:
        ips = set()
        for ip_str in _read_json_list(_blocked_ips_path):
            try:
                ips.add(str(ipaddress.ip_address(ip_str)))
            except Exception:
                continue
        _blocked_ips = ips

        nets: List[ipaddress._BaseNetwork] = []
        for cidr in _read_json_list(_blocked_cidrs_path):
            try:
                nets.append(ipaddress.ip_network(cidr, strict=False))
            except Exception:
                continue
        _blocked_networks = nets
        try:
            _last_mtime_ips = _blocked_ips_path.stat().st_mtime if _blocked_ips_path.exists() else 0.0
        except Exception:
            _last_mtime_ips = 0.0
        try:
            _last_mtime_cidrs = _blocked_cidrs_path.stat().st_mtime if _blocked_cidrs_path.exists() else 0.0
        except Exception:
            _last_mtime_cidrs = 0.0


def _ensure_fresh_blocklists() -> None:
    """Reload lists if underlying JSON files changed on disk."""
    try:
        m_ips = _blocked_ips_path.stat().st_mtime if _blocked_ips_path.exists() else 0.0
    except Exception:
        m_ips = 0.0
    try:
        m_c = _blocked_cidrs_path.stat().st_mtime if _blocked_cidrs_path.exists() else 0.0
    except Exception:
        m_c = 0.0
    if m_ips != _last_mtime_ips or m_c != _last_mtime_cidrs:
        _load_blocklists()


# Load on import
_load_blocklists()


def is_ip_blocked(ip: str) -> bool:
    """Return True if IP is in the local blocklists (exact or CIDR)."""
    _ensure_fresh_blocklists()
    try:
        obj = ipaddress.ip_address(ip)
    except Exception:
        # Non-parsable IPs are treated as blocked by policy
        return True

    with _cache_lock:
        if str(obj) in _blocked_ips:
            return True
        for net in _blocked_networks:
            if obj in net:
                return True
    return False


def mark_ip_blocked(ip: str) -> None:
    """Add an IP to the local blocked list and persist to JSON."""
    try:
        obj = ipaddress.ip_address(ip)
    except Exception:
        return
    ip_s = str(obj)
    with _cache_lock:
        if ip_s in _blocked_ips:
            return
        _blocked_ips.add(ip_s)
        _write_json_list(_blocked_ips_path, sorted(_blocked_ips))


def enforce_ip_allowed(ip: str) -> None:
    """Raise InvalidIP if the IP is blocked by local lists."""
    if is_ip_blocked(ip):
        raise InvalidIP("Blocked client IP")


def reload_blocklists() -> None:
    """Reload blocklists from disk into memory."""
    _load_blocklists()


# ---- Message content validation (no API key) ----
_IPV4_RX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def extract_ipv4(text: str) -> List[str]:
    t = text or ""
    found = set(m.group(0) for m in _IPV4_RX.finditer(t))
    return sorted(found)


def validate_ips_in_text(text: str) -> None:
    """Raise InvalidIP if text contains an IP present in local blocklists."""
    for ip_str in extract_ipv4(text):
        if is_ip_blocked(ip_str):
            raise InvalidIP("Blocked IP present in message")


