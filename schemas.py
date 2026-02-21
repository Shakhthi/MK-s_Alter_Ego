"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field


class PushoverPayload(BaseModel):
    """Validated payload for Pushover API (token, user, message)."""

    token: str = Field(..., min_length=1, description="Pushover API token")
    user: str = Field(..., min_length=1, description="Pushover user key")
    message: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        strip_whitespace=True,
        description="Message body (max 1024 chars)",
    )
