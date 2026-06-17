"""
renderers.py
------------
Convert Pydantic objects into formatted markdown strings for Streamlit display.
Keeps display logic completely separate from chain/LLM logic.
"""

from models import AssistantResponse, ConfirmationResponse


def render_response(r: AssistantResponse, query: str = "") -> str:
    parts = []

    if r.response_type == "eligibility":
        icon = {"Eligible": "✅", "Not Eligible": "❌", "Conditional Refund": "⚠️"}.get(r.verdict or "", "ℹ️")
        parts.append(f"### {icon} {r.verdict}\n\n{r.reason or ''}")
        if r.return_window:
            parts.append(f"**Return window:** {r.return_window}")
        if r.return_deadline:
            parts.append(f"**⏰ Deadline info:** {r.return_deadline}")
        if r.conditions:
            parts.append(f"**⚠️ Conditions:** {r.conditions}")
        if r.verdict != "Not Eligible":
            parts.append("*Need help raising the refund? Just ask how!*")

    elif r.response_type == "process":
        q = query.lower()
        if "exchange" in q:
            label = "Here's how to raise an exchange request:"
        elif "cancel" in q:
            label = "Here's how to cancel your order:"
        else:
            label = "Here's how to proceed:"
        steps = r.steps or []
        if steps:
            steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
            parts.append(f"**{label}**\n{steps_md}")
        else:
            parts.append(f"**{label}**\nPlease contact support for step-by-step assistance.")
        if r.processing_time:
            parts.append(f"**Processing time:** {r.processing_time}")

    elif r.response_type == "policy_info":
        parts.append("### 📋 Policy Details\n\n" + (r.policy_summary or ""))
        meta = []
        if r.return_window:        meta.append(f"**Return window:** {r.return_window}")
        if r.processing_time:      meta.append(f"**Processing time:** {r.processing_time}")
        if r.exchange_available:   meta.append(f"**Exchange available:** {r.exchange_available}")
        if r.cancellation_allowed: meta.append(f"**Cancellation allowed:** {r.cancellation_allowed}")
        if meta:
            parts.append("  |  ".join(meta))
        if r.eligible_conditions:
            parts.append("**✅ Eligible conditions:**\n" + "\n".join(f"- {c}" for c in r.eligible_conditions))
        if r.non_eligible_conditions:
            parts.append("**❌ Not eligible:**\n" + "\n".join(f"- {c}" for c in r.non_eligible_conditions))

    else:  # general
        parts.append(r.answer or "I found relevant information but couldn't format a response. Please try rephrasing.")

    return "\n\n".join(parts)


def render_confirmation(r: ConfirmationResponse) -> str:
    icon  = "✅" if r.approved else "❌"
    parts = [f"### {icon} {r.decision}\n\n{r.explanation}"]
    if r.next_steps:
        steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(r.next_steps))
        parts.append(f"{'**Next steps:**' if r.approved else '**What to do:**'}\n{steps}")
    if r.approved and r.processing_time:
        parts.append(f"**Processing time:** {r.processing_time}")
    return "\n\n".join(parts)
