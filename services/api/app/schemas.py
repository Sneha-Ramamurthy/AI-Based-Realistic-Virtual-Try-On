from typing import Optional

from pydantic import BaseModel, Field


class TryOnRequest(BaseModel):
    prompt: Optional[str] = Field(
        default=None,
        description="Optional user prompt describing the desired look or garment style.",
    )
