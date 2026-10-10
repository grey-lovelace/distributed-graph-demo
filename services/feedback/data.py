"""Loads the reviews from data/reviews.json at startup and keeps them in memory.

The GraphQL resolvers and the REST handlers both read from this file.
"""

import json
from pathlib import Path

with Path("data/reviews.json").open(encoding="utf-8") as file:
    all_reviews: list[dict] = json.load(file)

all_reviews.sort(key=lambda review: review["submittedAt"])


def find_reviews(session_id: str | None = None, speaker_id: str | None = None) -> list[dict]:
    return [
        review
        for review in all_reviews
        if (session_id is None or review["sessionId"] == session_id)
        and (speaker_id is None or review["speakerId"] == speaker_id)
    ]


def average(ratings: list[int]) -> float | None:
    """Returns the mean rounded to two decimal places, or None when there are no ratings."""
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings), 2)


def session_average_rating(session_id: str) -> float | None:
    return average([review["sessionRating"] for review in find_reviews(session_id=session_id)])


def speaker_average_rating(speaker_id: str) -> float | None:
    return average([review["speakerRating"] for review in find_reviews(speaker_id=speaker_id)])
