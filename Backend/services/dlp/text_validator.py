# services/dlp/text_validator.py
from typing import Literal
from .gemini_client import classify_is_baking_recipe, GeminiClientError

Decision = Literal["allow", "block"]

class DLPViolation(Exception):
    """נזרקת כשמדיניות מחליטה לחסום (לתרגום ל-HTTP 403 בשכבת ה-API)."""
    pass

# טריגר מקומי מהיר (עברית/אנגלית) כדי שלא נכה ב-API ללא צורך
_BAKING_HINTS = (
    "אפייה", "מתכון", "קמח", "אבקת אפייה", "חמאה", "ביצים", "סוכר",
    "תנור", "שמרים", "בצק", "לישה",
    "bake", "baking", "recipe", "flour", "butter", "egg", "sugar",
    "oven", "yeast", "dough", "proof"
)

def looks_suspicious_baking(text: str) -> bool:
    t = (text or "").lower()
    return any(h.lower() in t for h in _BAKING_HINTS)

async def decide_for_text(
    text: str,
    *,
    timeout_sec: float = 2.5,
    fail_closed: bool = True
) -> Decision:
    """
    החזרת החלטה סופית לטקסט:
    - 'allow' אם אין חשד או אם Gemini קבע שאינו מתכון
    - 'block' אם Gemini קבע שזה מתכון, או אם יש שגיאת ספק/טיים-אאוט (כש-fail_closed=True)
    """
    if not looks_suspicious_baking(text):
        return "allow"

    try:
        is_recipe = await classify_is_baking_recipe(text, timeout_sec=timeout_sec)
        return "block" if is_recipe else "allow"
    except GeminiClientError:
        return "block" if fail_closed else "allow"

def enforce_or_raise(decision: Decision) -> None:
    """נוחות: ממיר החלטה לחריגה במקרה חסימה."""
    if decision == "block":
        raise DLPViolation("DLP policy violation: baking recipe blocked")
