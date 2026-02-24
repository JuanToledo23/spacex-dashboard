"""Pydantic schemas for AI chat and fun fact endpoints."""

import re

from pydantic import BaseModel, field_validator

_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(previous|above|all)\s+instructions"
    r"|you\s+are\s+now"
    r"|system\s*:\s*"
    r"|<\|.*?\|>"
    r"|\[\s*INST\s*\])",
    re.IGNORECASE,
)

MAX_MESSAGE_LENGTH = 2000


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Enforce length limit and strip common prompt-injection patterns."""
        v = v[:MAX_MESSAGE_LENGTH]
        v = _INJECTION_PATTERNS.sub("", v).strip()
        return v


class ChatResponse(BaseModel):
    response: str


class AiStatusResponse(BaseModel):
    available: bool


class FunFactResponse(BaseModel):
    fact: str
