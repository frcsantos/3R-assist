"""FeedbackRepository — general site / product feedback."""

from __future__ import annotations

from app.db.connection import get_pool
from app.models.feedback import Feedback, FeedbackCreate


class FeedbackRepository:
    async def create(self, payload: FeedbackCreate) -> Feedback:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO feedback (user_id, url, object, feedback_text)
                VALUES ($1, $2, $3, $4)
                RETURNING id, user_id, url, object, feedback_text, created_at
                """,
                payload.user_id,
                payload.url.strip(),
                payload.object.strip(),
                payload.feedback_text.strip(),
            )
        return Feedback(
            id=row["id"],
            user_id=row["user_id"],
            url=row["url"],
            object=row["object"],
            feedback_text=row["feedback_text"],
            created_at=row["created_at"],
        )
