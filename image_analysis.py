"""
image_analysis.py
-----------------
Groq vision API calls for image proof analysis.
Reads GROQ_API_KEY from environment (HuggingFace Spaces Secret).
"""

import base64
import os
import httpx

# Reads from HuggingFace Spaces Secret — no .env needed
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

_PROOF_PROMPTS = {
    "food": (
        "You are a food quality inspector for refund verification.\n"
        "1. What food item is shown?\n"
        "2. Is there visible spoilage, mould, discolouration, or expiry evidence?\n"
        "3. Is the expiry date visible? If yes, state it.\n"
        "4. VERDICT: Start your final line with exactly CONFIRMED or NOT_CONFIRMED."
    ),
    "clothing": (
        "You are a clothing quality inspector for refund verification.\n"
        "1. What clothing item is shown?\n"
        "2. Visible tearing, ripping, loose stitching, holes, or manufacturing defects?\n"
        "3. Manufacturing defect or wear-and-tear?\n"
        "4. VERDICT: Start your final line with exactly CONFIRMED or NOT_CONFIRMED."
    ),
    "damage": (
        "You are a product damage inspector for refund verification.\n"
        "1. What product is shown?\n"
        "2. Visible physical damage — cracks, broken parts, burn marks?\n"
        "3. Manufacturing defect or user-caused?\n"
        "4. VERDICT: Start your final line with exactly CONFIRMED or NOT_CONFIRMED."
    ),
    "digital": (
        "You are a billing and subscription issue verifier for refund verification.\n"
        "Examine this screenshot carefully:\n"
        "1. What app or service is shown?\n"
        "2. Is there evidence of duplicate payment, failed activation, or billing error?\n"
        "3. Are there transaction IDs, error messages, or payment amounts visible? State them.\n"
        "4. VERDICT: Start your final line with exactly CONFIRMED or NOT_CONFIRMED."
    ),
}


def encode_image_to_base64(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


def _vision_call(image_b64: str, media_type: str, prompt_text: str) -> str:
    payload = {
        "model": _VISION_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}},
            {"type": "text", "text": prompt_text},
        ]}],
        "max_tokens": 512,
        "temperature": 0,
    }
    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def analyze_proof_image(image_b64: str, media_type: str, proof_category: str) -> dict:
    prompt   = _PROOF_PROMPTS.get(proof_category, _PROOF_PROMPTS["damage"])
    text     = _vision_call(image_b64, media_type, prompt)
    verified = "CONFIRMED" in text.upper() and "NOT_CONFIRMED" not in text.upper()
    return {
        "description": text,
        "verified":    verified,
        "verdict":     "✅ CONFIRMED" if verified else "❌ NOT CONFIRMED",
    }
