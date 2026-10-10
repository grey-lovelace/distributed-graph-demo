"""Resolves the fields in schema.graphql."""

from ariadne import ObjectType, QueryType, load_schema_from_path
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema

import data

query = QueryType()
review = ObjectType("Review")

# FederatedObjectType marks a type that has a @key in the schema.
# These two types are entities that other subgraphs own. This subgraph adds fields to them.
session = FederatedObjectType("Session")
speaker = FederatedObjectType("Speaker")


@query.field("reviews")
def resolve_reviews(_, info, sessionId=None, speakerId=None):
    return data.find_reviews(session_id=sessionId, speaker_id=speakerId)


# The router calls a reference resolver with a representation such as {"__typename": "Session", "id": "session-12"}.
# This subgraph needs only the id, so it returns the representation as it is.
@session.reference_resolver
def resolve_session_reference(_, info, representation):
    return representation


@session.field("reviews")
def resolve_session_reviews(session_ref, info):
    return data.find_reviews(session_id=session_ref["id"])


@session.field("averageRating")
def resolve_session_average_rating(session_ref, info):
    return data.session_average_rating(session_ref["id"])


@session.field("reviewCount")
def resolve_session_review_count(session_ref, info):
    return len(data.find_reviews(session_id=session_ref["id"]))


@speaker.reference_resolver
def resolve_speaker_reference(_, info, representation):
    return representation


@speaker.field("averageRating")
def resolve_speaker_average_rating(speaker_ref, info):
    return data.speaker_average_rating(speaker_ref["id"])


# A review stores only the session ID and the speaker ID. Each of these resolvers returns an entity reference.
# The router uses the id to fetch the session and the speaker from the subgraphs that own them.
@review.field("session")
def resolve_review_session(review_row, info):
    return {"id": review_row["sessionId"]}


@review.field("speaker")
def resolve_review_speaker(review_row, info):
    return {"id": review_row["speakerId"]}


# make_federated_schema turns the schema into a Federation subgraph.
# It adds the _service and _entities fields that the router calls.
schema = make_federated_schema(
    load_schema_from_path("schema.graphql"),
    query,
    review,
    session,
    speaker,
)
