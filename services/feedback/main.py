from ariadne.asgi import GraphQL
from fastapi import FastAPI

import rest
from resolvers import schema

app = FastAPI(
    title="Feedback API",
    version="1.0.0",
    description="Attendee reviews of conference sessions and speakers.",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# GraphQL subgraph
app.add_route("/graphql", GraphQL(schema), methods=["GET", "POST"])

# REST API. FastAPI generates /openapi.json and the Swagger UI at /docs from it.
app.include_router(rest.router)
