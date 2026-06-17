"""
utils.py
--------
Pure helper functions — no LLM, no DB.
  - Greeting detection
  - Query category detection
  - Image proof keyword detection
  - Proof category detection (food / clothing / damage / digital)
"""

import re

# ── Greeting detection ─────────────────────────────────────────────────────────
_GREETING_ROOTS = [
    "hi", "hello", "hey", "hiya", "howdy", "greetings",
    "good morning", "good afternoon", "good evening", "good night",
    "whats up", "what's up", "sup", "yo",
    "thanks", "thank you", "ty", "thx",
    "bye", "goodbye", "see you", "take care",
    "ok", "okay",
]

def is_greeting(text: str) -> bool:
    t = text.strip().lower().rstrip("!?., ")
    collapsed = re.sub(r"(.)\1+", r"\1", t)
    for g in _GREETING_ROOTS:
        for s in (t, collapsed):
            if s == g or s.startswith(g + " ") or s.startswith(g + ","):
                return True
    return False


# ── Query category detection ───────────────────────────────────────────────────
def get_query_category(q: str) -> str:
    q = q.lower()
    if any(x in q for x in ["food", "meal", "spoiled", "expired", "rotten", "stale", "quickbite"]):
        return "food"
    if any(x in q for x in ["shirt", "clothes", "clothing", "jeans", "tshirt", "dress", "torn", "fabric", "stylehub"]):
        return "clothing"
    if any(x in q for x in ["phone", "mobile", "laptop", "tv", "electronics", "device", "gadget", "broken", "cracked", "defective", "techzone"]):
        return "electronics"
    if any(x in q for x in ["book", "novel", "pages", "booknest"]):
        return "books"
    if any(x in q for x in ["sportswear", "sports", "shoe", "jersey", "sportflex"]):
        return "sportswear"
    if any(x in q for x in ["subscription", "digital", "streaming", "streamprime"]):
        return "digital"
    if any(x in q for x in ["dailymart", "household", "general"]):
        return "general"
    return ""


# ── Proof keyword detection ────────────────────────────────────────────────────
_PROOF_KEYWORDS = [
    # Physical damage
    "broken", "cracked", "damaged", "damage", "shattered",
    "leaking", "burnt", "scratched", "dented",
    # Device issues
    "not working", "faulty", "malfunctioning", "dead on arrival",
    # Defect
    "defective", "defect", "manufacturing defect",
    # Food spoilage
    "spoiled", "spoilt", "rotten", "stale", "mouldy", "mold",
    "mould", "bad smell", "discoloured", "expired food", "expired",
    # Clothing damage
    "torn", "ripped", "stitching", "hole", "faded", "worn out",
    # Book damage
    "missing pages", "damaged cover",
    # Wrong / incorrect item
    "wrong item", "incorrect item", "incorrect order", "wrong order",
    "different item", "different product", "got different",
    "ordered but got", "but received", "but got",
    "instead of", "in place of", "i ordered", "i got",
    # Missing item
    "missing item", "missing product", "item missing", "item not received",
    # Combined
    "received damaged", "arrived damaged", "got damaged",
    "got defective", "received defective",
    "got spoiled", "received spoiled", "i got spoiled",
]

def needs_image_proof_local(query: str) -> bool:
    """True for any physical or wrong/missing item claim — proof required to prevent fraud."""
    return any(kw in query.lower() for kw in _PROOF_KEYWORDS)


# ── Proof category detection ───────────────────────────────────────────────────
def detect_proof_category(query: str, company: str = "") -> str:
    """
    Detect what kind of proof image to expect.
    StreamPrime (digital) needs a screenshot, others need a photo.
    """
    q = query.lower()
    if company.lower() == "streamprime" or any(x in q for x in [
        "subscription", "digital", "streaming", "billing",
        "activation", "duplicate payment", "streamprime"
    ]):
        return "digital"
    if any(x in q for x in ["food", "meal", "spoiled", "expired", "rotten", "stale", "mouldy"]):
        return "food"
    if any(x in q for x in ["shirt", "clothes", "dress", "torn", "ripped", "fabric", "jeans", "stitching"]):
        return "clothing"
    return "damage"
