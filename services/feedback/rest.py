"""Serves the reviews as a REST API under /api."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

import data

router = APIRouter(prefix="/api")


class Review(BaseModel):
    """One attendee's review of one session and one of its speakers."""

    id: str = Field(description="The unique review ID.", examples=["review-042"])
    sessionId: str = Field(
        description="The ID of the reviewed session. Look it up with GET /api/sessions/{id} on the Sessions API.",
        examples=["session-12"],
    )
    speakerId: str = Field(
        description="The ID of the rated speaker. Look it up with GET /api/speakers/{id} on the Speakers API.",
        examples=["speaker-07"],
    )
    sessionRating: int = Field(ge=1, le=5, description="The rating of the session content, from 1 (poor) to 5 (excellent).")
    speakerRating: int = Field(ge=1, le=5, description="The rating of the speaker's delivery, from 1 (poor) to 5 (excellent).")
    comment: str | None = Field(description="An optional free-text comment. It is null when the attendee left no comment.")
    submittedAt: str = Field(
        description="The moment the review was submitted, as an ISO 8601 date-time in UTC.",
        examples=["2026-11-12T15:02:00Z"],
    )


class SessionRatingSummary(BaseModel):
    """The rating summary for one session."""

    sessionId: str = Field(description="The ID of the session.", examples=["session-12"])
    averageRating: float | None = Field(
        description="The mean session rating from 1.0 to 5.0, rounded to two decimal places. It is null when there are no reviews."
    )
    reviewCount: int = Field(description="The number of reviews of the session.")


class SpeakerRatingSummary(BaseModel):
    """The rating summary for one speaker, across all of their sessions."""

    speakerId: str = Field(description="The ID of the speaker.", examples=["speaker-07"])
    averageRating: float | None = Field(
        description="The mean speaker rating from 1.0 to 5.0, rounded to two decimal places. It is null when there are no reviews."
    )
    reviewCount: int = Field(description="The number of reviews that rate the speaker.")


@router.get("/reviews", operation_id="listReviews", summary="List reviews sorted by submission time. Both filters are optional, and they combine with AND.")
def list_reviews(sessionId: str | None = None, speakerId: str | None = None) -> list[Review]:
    return data.find_reviews(session_id=sessionId, speaker_id=speakerId)


@router.get("/sessions/{id}/rating-summary", operation_id="getSessionRatingSummary", summary="Get the average rating and review count for one session.")
def get_session_rating_summary(id: str) -> SessionRatingSummary:
    return SessionRatingSummary(
        sessionId=id,
        averageRating=data.session_average_rating(id),
        reviewCount=len(data.find_reviews(session_id=id)),
    )


@router.get("/speakers/{id}/rating-summary", operation_id="getSpeakerRatingSummary", summary="Get the average rating and review count for one speaker.")
def get_speaker_rating_summary(id: str) -> SpeakerRatingSummary:
    return SpeakerRatingSummary(
        speakerId=id,
        averageRating=data.speaker_average_rating(id),
        reviewCount=len(data.find_reviews(speaker_id=id)),
    )
