"""
models.py
---------
Pydantic output schemas for LLM structured responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class AssistantResponse(BaseModel):
    """
    Single unified output schema for all question types.
    The LLM picks response_type and fills the relevant fields.
    """
    response_type: str = Field(
        description="Must be exactly one of: 'eligibility' | 'process' | 'policy_info' | 'general'"
    )
    # ── eligibility ───────────────────────────────────────────────────────────
    verdict: Optional[str] = Field(
        default=None,
        description="Only for eligibility. One of: 'Eligible', 'Not Eligible', 'Conditional Refund'."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Only for eligibility. 2-3 sentence plain-English explanation."
    )
    return_window: Optional[str] = Field(
        default=None,
        description="Return / refund window e.g. '7 days'. Use for eligibility and policy_info."
    )
    conditions: Optional[str] = Field(
        default=None,
        description="Important conditions or exceptions for eligibility."
    )
    return_deadline: Optional[str] = Field(
        default=None,
        description=(
            "Only when the return window has PASSED. "
            "E.g. 'The 7-day return window has passed.' "
            "Leave null if window has not passed or is unknown."
        )
    )
    needs_image_proof: bool = Field(
        default=False,
        description="True for all physical claims: damage, defect, spoilage, wrong item, missing item."
    )
    # ── process ───────────────────────────────────────────────────────────────
    steps: List[str] = Field(
        default_factory=list,
        description=(
            "Only for process. Exact numbered steps from PROCESS CONTEXT. "
            "Exchange question -> exchange steps. Cancel -> cancellation steps. Refund -> refund steps."
        )
    )
    processing_time: Optional[str] = Field(
        default=None,
        description="Processing time. Use for process and policy_info."
    )
    # ── policy_info ───────────────────────────────────────────────────────────
    policy_summary: Optional[str] = Field(
        default=None,
        description="Only for policy_info. Short plain-English summary of the policy."
    )
    exchange_available: Optional[str] = Field(
        default=None,
        description="Only for policy_info. 'Yes' or 'No'."
    )
    cancellation_allowed: Optional[str] = Field(
        default=None,
        description="Only for policy_info. 'Yes' or 'No'."
    )
    eligible_conditions: List[str] = Field(
        default_factory=list,
        description="Only for policy_info. Full list of eligible conditions."
    )
    non_eligible_conditions: List[str] = Field(
        default_factory=list,
        description="Only for policy_info. Full list of non-eligible conditions."
    )
    # ── general / fallback ────────────────────────────────────────────────────
    answer: Optional[str] = Field(
        default=None,
        description="For response_type='general'. Answer directly from context."
    )

    @model_validator(mode="after")
    def coerce_null_lists(self):
        if self.steps is None:
            self.steps = []
        if self.eligible_conditions is None:
            self.eligible_conditions = []
        if self.non_eligible_conditions is None:
            self.non_eligible_conditions = []
        return self


class ConfirmationResponse(BaseModel):
    """Structured output after image proof has been analyzed."""
    approved: bool = Field(description="True if refund approved based on image.")
    decision: str  = Field(description="'Refund Approved' or 'Refund Not Approved'")
    explanation: str = Field(description="Short explanation based on the image.")
    next_steps: List[str] = Field(
        default_factory=list,
        description="Steps to complete refund (approved) or what to do next (rejected)."
    )
    processing_time: Optional[str] = Field(
        default=None,
        description="Processing time if approved."
    )
