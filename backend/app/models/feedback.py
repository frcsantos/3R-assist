from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    url: str = Field(min_length=1)
    object: str = Field(min_length=1)
    feedback_text: str = Field(min_length=1)
    user_id: int | None = None
    # Used only as the subject of the forwarded contact email; not stored.
    subject: str | None = Field(default=None, max_length=200)


class Feedback(BaseModel):
    id: int
    user_id: int | None = None
    url: str
    object: str
    feedback_text: str
    created_at: datetime
