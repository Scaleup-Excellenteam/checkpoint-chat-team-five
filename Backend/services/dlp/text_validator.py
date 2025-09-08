from typing import Literal
from core.config import settings
try:
    # Prefer Ollama (local, fast)
    from .ollama_client import classify_is_baking_recipe, OllamaClientError as ProviderError
except Exception:
    # Fallback to Gemini client if Ollama import fails
    from .gemini_client import classify_is_baking_recipe, GeminiClientError as ProviderError
Decision = Literal["allow", "block"]
class DLPViolation(Exception):
    """Raised when policy decides to block (map to HTTP 403 at the API layer)."""
    pass
# Fast local trigger (English-heavy) so we call Gemini only when needed
_BAKING_HINTS = tuple(x.lower() for x in (
    # general intent
    "bake","baking","recipe","instructions","homemade",
    # ingredients
    "flour","sugar","brown sugar","butter","egg","eggs","milk","yeast","water",
    "salt","vanilla","vanilla extract","cocoa","cocoa powder","chocolate",
    "baking powder","baking soda","buttermilk","oil","olive oil","honey",
    "cream","heavy cream","cream cheese","powdered sugar","icing sugar",
    # measurements / tools
    "cup","cups","tablespoon","tbsp","teaspoon","tsp","gram","grams","ml",
    "mix","mixing","whisk","bowl","spatula","rolling pin","parchment",
    # actions / steps
    "preheat","oven","temperature","fahrenheit","celsius","knead","fold",
    "proof","proofing","rest","rise","ferment","let it rest","cool",
    # bakeware
    "pan","sheet","tray","loaf pan","cake pan","springform","muffin tin",
    # products / outputs
    "cake","cupcake","muffin","cookies","cookie","brownie","bread","baguette",
    "sourdough","crust","crumb","shortbread","pie","crust","tart","scone",
    "bun","roll","glaze","frosting","icing","buttercream","ganache",
))
def looks_suspicious_baking(text: str) -> bool:
    t = (text or "").lower()
    return any(hint in t for hint in _BAKING_HINTS)


def contains_blocked_keywords(text: str) -> bool:
    if not settings.BLOCKED_TEXT_KEYWORDS:
        return False
    t = (text or "").lower()
    return any(k in t for k in settings.BLOCKED_TEXT_KEYWORDS)
async def decide_for_text(
    text: str,
    *,
    timeout_sec: float = 2.5,
    fail_closed: bool = True
) -> Decision:
    """
    Final decision for a message text:
    - 'allow' if no suspicion or Gemini says it's not a baking recipe
    - 'block' if Gemini says it IS a recipe, or provider error/timeout (when fail_closed=True)
    """
    if contains_blocked_keywords(text):
        return "block"
    if not looks_suspicious_baking(text):
        return "allow"
    try:
        is_recipe = await classify_is_baking_recipe(text, timeout_sec=timeout_sec)
        return "block" if is_recipe else "allow"
    except ProviderError:
        return "block" if fail_closed else "allow"
def enforce_or_raise(decision: Decision) -> None:
    """Small helper: turn decision into an exception when blocking."""
    if decision == "block":
        raise DLPViolation("DLP policy violation: baking recipe blocked")