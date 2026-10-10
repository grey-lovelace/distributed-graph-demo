"""Writes the JSON data files for all four services into this folder.

Run it from the repository root:

    python3 data/seed.py

The random generator uses a fixed seed, so every run writes identical files.
The script uses only the Python standard library.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
rng = random.Random(2026)

# The conference runs on two days in London. London is on UTC in November,
# so every timestamp below is written in UTC with a "Z" suffix.
DAYS = ["2026-11-12", "2026-11-13"]

# Each slot is (start time, end time, IDs of the rooms in use).
# The Main Hall (room-01) is used in every slot.
SLOTS = [
    ("09:00", "09:45", ["room-01", "room-04"]),
    ("10:00", "10:45", ["room-01", "room-02", "room-05"]),
    ("11:15", "12:00", ["room-01", "room-03", "room-06"]),
    ("13:30", "14:15", ["room-01", "room-02", "room-04", "room-05"]),
    ("14:30", "15:15", ["room-01", "room-02", "room-03", "room-06"]),
    ("16:00", "16:45", ["room-01", "room-02", "room-03", "room-04"]),
]

# ---------------------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------------------

ROOMS = [
    {"id": "room-01", "name": "Main Hall", "floor": 0, "capacity": 800, "hasStreaming": True},
    {"id": "room-02", "name": "Riverside Theatre", "floor": 1, "capacity": 420, "hasStreaming": True},
    {"id": "room-03", "name": "Gallery Room", "floor": 1, "capacity": 210, "hasStreaming": True},
    {"id": "room-04", "name": "Workshop A", "floor": 2, "capacity": 120, "hasStreaming": False},
    {"id": "room-05", "name": "Workshop B", "floor": 2, "capacity": 80, "hasStreaming": False},
    {"id": "room-06", "name": "Library Room", "floor": 3, "capacity": 40, "hasStreaming": False},
]

# ---------------------------------------------------------------------------
# Speakers
# ---------------------------------------------------------------------------

TRACK_TOPICS = {
    "ARCHITECTURE": ["GraphQL Federation", "API design", "Microservices", "Domain-driven design", "Event-driven systems"],
    "AI": ["AI agents", "Model Context Protocol", "LLM evaluation", "Retrieval-augmented generation", "Prompt engineering"],
    "DEVELOPER_EXPERIENCE": ["Developer portals", "API documentation", "Code generation", "Testing", "Onboarding"],
    "PLATFORM": ["Kubernetes", "Observability", "API gateways", "Performance", "Security"],
    "DATA": ["Data modeling", "Streaming", "Caching", "Search", "Data governance"],
}

# Each speaker is (name, job title, company, company type, primary track).
SPEAKERS = [
    ("Amara Okafor", "Principal Consultant", "Northwind Consulting", "CONSULTANCY", "ARCHITECTURE"),
    ("Lukas Brandt", "Staff Engineer", "Parcelly", "PRODUCT", "ARCHITECTURE"),
    ("Priya Raman", "Chief Architect", "Meridian Bank", "ENTERPRISE", "ARCHITECTURE"),
    ("Tomás Ferreira", "API Lead", "Brightline Partners", "CONSULTANCY", "ARCHITECTURE"),
    ("Hannah Cole", "Platform Architect", "Atlas Logistics", "ENTERPRISE", "ARCHITECTURE"),
    ("Kenji Watanabe", "Engineering Manager", "Tidepool", "PRODUCT", "ARCHITECTURE"),
    ("Sofia Marchetti", "AI Engineering Lead", "Lumen Labs", "PRODUCT", "AI"),
    ("Daniel Mensah", "Director of AI Practice", "Northwind Consulting", "CONSULTANCY", "AI"),
    ("Grace Liu", "Machine Learning Engineer", "Open Health Alliance", "NONPROFIT", "AI"),
    ("Mateo Alvarez", "Senior Consultant", "Keystone Digital", "CONSULTANCY", "AI"),
    ("Aisha Rahman", "Head of Applied AI", "Meridian Bank", "ENTERPRISE", "AI"),
    ("Oliver Grant", "Founder", "Promptwise", "PRODUCT", "AI"),
    ("Chloe Dubois", "Developer Advocate", "Parcelly", "PRODUCT", "DEVELOPER_EXPERIENCE"),
    ("Samuel Adeyemi", "Developer Experience Lead", "Atlas Logistics", "ENTERPRISE", "DEVELOPER_EXPERIENCE"),
    ("Ingrid Larsen", "Technical Writer", "Code for Communities", "NONPROFIT", "DEVELOPER_EXPERIENCE"),
    ("Ravi Patel", "Principal Engineer", "Brightline Partners", "CONSULTANCY", "DEVELOPER_EXPERIENCE"),
    ("Emily Novak", "Staff Developer Advocate", "Tidepool", "PRODUCT", "DEVELOPER_EXPERIENCE"),
    ("Yusuf Demir", "Engineering Director", "Civic Transit Authority", "ENTERPRISE", "DEVELOPER_EXPERIENCE"),
    ("Marta Kowalski", "SRE Lead", "Lumen Labs", "PRODUCT", "PLATFORM"),
    ("Jonas Weber", "Cloud Architect", "Keystone Digital", "CONSULTANCY", "PLATFORM"),
    ("Fatima Zahra", "Security Engineer", "Meridian Bank", "ENTERPRISE", "PLATFORM"),
    ("Liam O'Connor", "Platform Engineer", "Open Health Alliance", "NONPROFIT", "PLATFORM"),
    ("Mei Chen", "Performance Engineer", "Promptwise", "PRODUCT", "PLATFORM"),
    ("Carlos Mendes", "Infrastructure Manager", "Atlas Logistics", "ENTERPRISE", "PLATFORM"),
    ("Nadia Petrova", "Data Architect", "Northwind Consulting", "CONSULTANCY", "DATA"),
    ("Ethan Brooks", "Data Engineer", "Parcelly", "PRODUCT", "DATA"),
    ("Zainab Yusuf", "Head of Data", "Civic Transit Authority", "ENTERPRISE", "DATA"),
    ("Hugo Laurent", "Search Engineer", "Tidepool", "PRODUCT", "DATA"),
    ("Ana Costa", "Data Consultant", "Brightline Partners", "CONSULTANCY", "DATA"),
    ("Peter Lindqvist", "Volunteer Data Lead", "Code for Communities", "NONPROFIT", "DATA"),
]

COMPANY_DESCRIPTIONS = {
    "CONSULTANCY": "helps clients",
    "PRODUCT": "builds products that help teams",
    "ENTERPRISE": "helps a large organisation",
    "NONPROFIT": "helps a non-profit organisation",
}


def make_speakers():
    speakers = []
    for index, (name, title, company, company_type, track) in enumerate(SPEAKERS, start=1):
        topics = rng.sample(TRACK_TOPICS[track], 3)
        first_name = name.split(" ")[0]
        bio = (
            f"{name} is a {title.lower()} at {company}. "
            f"{first_name} {COMPANY_DESCRIPTIONS[company_type]} with {topics[0].lower()} and {topics[1].lower()}."
        )
        speakers.append({
            "id": f"speaker-{index:02d}",
            "name": name,
            "title": title,
            "company": company,
            "companyType": company_type,
            "bio": bio,
            "topics": topics,
            "_track": track,
            "_quality": rng.uniform(3.0, 4.7),
        })
    return speakers


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

# Each session is (title, track, level, abstract).
SESSION_IDEAS = [
    ("One Graph, Many Teams", "ARCHITECTURE", "BEGINNER",
     "How independent teams publish subgraphs that compose into a single API."),
    ("Entities Explained", "ARCHITECTURE", "INTERMEDIATE",
     "A walk through keys, reference resolvers, and how the router joins data across services."),
    ("Migrating a Monolith to a Supergraph", "ARCHITECTURE", "ADVANCED",
     "Lessons from moving a ten-year-old REST monolith behind a federated graph one field at a time."),
    ("Designing Schemas for Change", "ARCHITECTURE", "INTERMEDIATE",
     "Patterns for evolving a schema without breaking clients."),
    ("Event-Driven Meets Graph", "ARCHITECTURE", "ADVANCED",
     "Combining event streams and a federated graph without duplicating data."),
    ("The Bounded Context Is Your Subgraph", "ARCHITECTURE", "BEGINNER",
     "Using domain-driven design to decide where one subgraph ends and the next begins."),
    ("Query Plans Under the Microscope", "ARCHITECTURE", "ADVANCED",
     "Reading router query plans to find slow joins and fix them."),
    ("REST and GraphQL Side by Side", "ARCHITECTURE", "BEGINNER",
     "When to keep a REST API, when to add a graph, and how to run both."),
    ("Agents Need Good APIs", "AI", "BEGINNER",
     "Why the quality of an API decides how well an AI agent can use it."),
    ("Building Tools for the Model Context Protocol", "AI", "INTERMEDIATE",
     "Turning existing GraphQL operations into MCP tools that an agent can call."),
    ("Evaluating Agents in Production", "AI", "ADVANCED",
     "Measuring agent accuracy, cost, and latency once real users arrive."),
    ("Retrieval Without the Hype", "AI", "INTERMEDIATE",
     "A practical guide to retrieval-augmented generation over company data."),
    ("Prompting Is Interface Design", "AI", "BEGINNER",
     "Treating prompts, tool descriptions, and schema descriptions as user interface."),
    ("Guardrails for Enterprise Agents", "AI", "ADVANCED",
     "Access control, auditing, and rate limits for agents that touch real systems."),
    ("Small Models, Big Wins", "AI", "INTERMEDIATE",
     "Where smaller language models beat larger ones on cost and speed."),
    ("From Chatbot to Coworker", "AI", "BEGINNER",
     "Case studies of agents that complete multi-step tasks across several APIs."),
    ("Docs That Developers Actually Read", "DEVELOPER_EXPERIENCE", "BEGINNER",
     "Writing API documentation that answers real questions."),
    ("Generated Clients Done Right", "DEVELOPER_EXPERIENCE", "INTERMEDIATE",
     "Using code generation to give every team a typed client."),
    ("Your Portal Is a Product", "DEVELOPER_EXPERIENCE", "BEGINNER",
     "Running an internal developer portal with product management habits."),
    ("Contract Testing for Subgraphs", "DEVELOPER_EXPERIENCE", "ADVANCED",
     "Catching breaking schema changes in CI before they reach the router."),
    ("The First Hour of Onboarding", "DEVELOPER_EXPERIENCE", "BEGINNER",
     "Measuring and shortening the time it takes a new developer to make a first API call."),
    ("Mocking the Whole Graph", "DEVELOPER_EXPERIENCE", "INTERMEDIATE",
     "Building realistic local environments for a federated API."),
    ("Error Messages Are UX", "DEVELOPER_EXPERIENCE", "INTERMEDIATE",
     "Designing errors that help both humans and AI agents recover."),
    ("Inner Source for APIs", "DEVELOPER_EXPERIENCE", "ADVANCED",
     "Letting any team contribute to a shared graph without losing control."),
    ("Running the Router at Scale", "PLATFORM", "ADVANCED",
     "Capacity planning, autoscaling, and tuning for a high-traffic router."),
    ("Observability for Distributed Graphs", "PLATFORM", "INTERMEDIATE",
     "Tracing one request across the router and every subgraph it touches."),
    ("Zero-Trust APIs", "PLATFORM", "ADVANCED",
     "Authentication and authorization patterns for a federated API."),
    ("Kubernetes for API Teams", "PLATFORM", "BEGINNER",
     "The minimum Kubernetes knowledge an API team needs."),
    ("Caching Across Subgraphs", "PLATFORM", "INTERMEDIATE",
     "Entity caching, cache hints, and what to never cache."),
    ("Gateways Compared", "PLATFORM", "BEGINNER",
     "API gateways, service meshes, and graph routers, and where each one fits."),
    ("Performance Budgets for APIs", "PLATFORM", "INTERMEDIATE",
     "Setting and enforcing latency budgets per field and per service."),
    ("Incident Review: The Day the Graph Went Down", "PLATFORM", "INTERMEDIATE",
     "A candid review of a real outage and the changes that followed."),
    ("Modeling Data for a Graph", "DATA", "BEGINNER",
     "Turning tables and documents into types and relationships."),
    ("Streaming Data into GraphQL", "DATA", "ADVANCED",
     "Serving fresh data from Kafka through subscriptions and deferred fields."),
    ("Search as a Subgraph", "DATA", "INTERMEDIATE",
     "Exposing a search engine through the graph with relevance intact."),
    ("Governing Shared Data", "DATA", "INTERMEDIATE",
     "Ownership, lineage, and policy for data that many teams read."),
    ("The Cost of a Join", "DATA", "ADVANCED",
     "Batching, data loaders, and the N+1 problem in federated systems."),
    ("Open Data for Public Good", "DATA", "BEGINNER",
     "How a non-profit publishes open datasets through a public graph."),
    ("Analytics on the Graph", "DATA", "INTERMEDIATE",
     "Using operation metrics to learn how clients really use your data."),
    ("Data Contracts in Practice", "DATA", "ADVANCED",
     "Agreeing on data shape between producers and consumers, and keeping the agreement."),
]


def make_slots():
    """Returns every (day, start, end, room) combination that holds a session."""
    slots = []
    for day in DAYS:
        for start, end, room_ids in SLOTS:
            for room_id in room_ids:
                slots.append((day, start, end, room_id))
    return slots


def make_sessions(speakers):
    slots = make_slots()
    ideas = SESSION_IDEAS[:]
    rng.shuffle(ideas)

    sessions = []
    for index, ((day, start, end, room_id), (title, track, level, abstract)) in enumerate(zip(slots, ideas), start=1):
        sessions.append({
            "id": f"session-{index:02d}",
            "title": title,
            "abstract": abstract,
            "track": track,
            "level": level,
            "startsAt": f"{day}T{start}:00Z",
            "endsAt": f"{day}T{end}:00Z",
            "speakerIds": [],
            "roomId": room_id,
        })

    # Give every speaker one session in their own track first.
    # Then give the remaining sessions a speaker from the same track.
    for track in TRACK_TOPICS:
        track_speakers = [s for s in speakers if s["_track"] == track]
        track_sessions = [s for s in sessions if s["track"] == track]
        rng.shuffle(track_speakers)
        for position, session in enumerate(track_sessions):
            session["speakerIds"].append(track_speakers[position % len(track_speakers)]["id"])

    # About a third of the sessions get a co-speaker from the same track.
    for session in sessions:
        if rng.random() < 0.35:
            candidates = [
                s["id"] for s in speakers
                if s["_track"] == session["track"] and s["id"] not in session["speakerIds"]
            ]
            session["speakerIds"].append(rng.choice(candidates))

    # The Main Hall afternoon sessions on day one are the ones the demo question asks about.
    # Each of them gets a consultancy co-speaker, so the answer includes consultancies.
    for session in sessions:
        if is_main_hall_afternoon_day_one(session) and not has_consultancy_speaker(session, speakers):
            consultants = [
                s["id"] for s in speakers
                if s["_track"] == session["track"] and s["companyType"] == "CONSULTANCY"
            ]
            session["speakerIds"].append(rng.choice(consultants))

    for session in sessions:
        session["speakerIds"].sort()

    return sessions


def is_main_hall_afternoon_day_one(session):
    return (
        session["roomId"] == "room-01"
        and session["startsAt"].startswith(DAYS[0])
        and session["startsAt"][11:16] >= "12:00"
    )


def has_consultancy_speaker(session, speakers):
    by_id = {s["id"]: s for s in speakers}
    return any(by_id[i]["companyType"] == "CONSULTANCY" for i in session["speakerIds"])


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

# A bigger room has a bigger audience, so its sessions get more reviews.
REVIEW_COUNT_RANGE = {
    "room-01": (14, 19),
    "room-02": (9, 12),
    "room-03": (7, 9),
    "room-04": (5, 7),
    "room-05": (3, 5),
    "room-06": (2, 3),
}

# Fixed quality scores for the Main Hall afternoon sessions on day one.
# They make sure the demo question has a clear spread of ratings.
MAIN_HALL_AFTERNOON_QUALITY = [4.7, 2.6, 4.2]

COMMENTS = {
    1: ["Not what the abstract promised.", "Hard to follow.", "The audio was poor and the slides were unreadable."],
    2: ["The examples did not match my use case.", "Interesting topic, weak delivery.", "Ran out of time before the good part."],
    3: ["Solid overview.", "Some useful ideas.", "Good content, but it went too fast."],
    4: ["Clear and practical.", "Great examples.", "I will try this at work next week."],
    5: ["Best talk of the day.", "Brilliant demo.", "Exactly what I came here to learn."],
}


def clamp_rating(value):
    return max(1, min(5, round(value)))


def make_reviews(sessions, speakers):
    speaker_quality = {s["id"]: s["_quality"] for s in speakers}

    main_hall_afternoon = [s for s in sessions if is_main_hall_afternoon_day_one(s)]

    reviews = []
    for session in sessions:
        quality = rng.uniform(2.8, 4.6)
        if session in main_hall_afternoon:
            quality = MAIN_HALL_AFTERNOON_QUALITY[main_hall_afternoon.index(session)]

        low, high = REVIEW_COUNT_RANGE[session["roomId"]]
        count = rng.randint(low, high)

        # The last session of the conference has no reviews yet.
        # This shows that averageRating is null when there are no reviews.
        if session is sessions[-1]:
            count = 0

        ends_at = datetime.fromisoformat(session["endsAt"].replace("Z", "+00:00"))
        for _ in range(count):
            speaker_id = rng.choice(session["speakerIds"])
            session_rating = clamp_rating(rng.gauss(quality, 0.8))
            speaker_rating = clamp_rating(rng.gauss((quality + speaker_quality[speaker_id]) / 2, 0.8))
            submitted_at = ends_at + timedelta(minutes=rng.randint(2, 600))
            comment = rng.choice(COMMENTS[session_rating]) if rng.random() < 0.7 else None
            reviews.append({
                "sessionId": session["id"],
                "speakerId": speaker_id,
                "sessionRating": session_rating,
                "speakerRating": speaker_rating,
                "comment": comment,
                "submittedAt": submitted_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })

    reviews.sort(key=lambda r: (r["submittedAt"], r["sessionId"]))
    return [{"id": f"review-{index:03d}", **review} for index, review in enumerate(reviews, start=1)]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_json(file_name, rows):
    path = DATA_DIR / file_name
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows):>3} records to data/{file_name}")


def public(rows):
    """Removes the private generator fields, which start with an underscore."""
    return [{k: v for k, v in row.items() if not k.startswith("_")} for row in rows]


def main():
    speakers = make_speakers()
    sessions = make_sessions(speakers)
    reviews = make_reviews(sessions, speakers)

    write_json("speakers.json", public(speakers))
    write_json("rooms.json", ROOMS)
    write_json("sessions.json", sessions)
    write_json("reviews.json", reviews)


if __name__ == "__main__":
    main()
