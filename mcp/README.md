# MCP servers

This folder holds the MCP servers that give an AI agent access to the conference platform.
An agent can use the graph through one GraphQL MCP server, or use the REST APIs through four
REST MCP servers, one for each service. The same question asked both ways shows how much work
each style leaves to the agent.

## Run them

The MCP servers connect to the main stack, so start that first. Then run this from the repository root:

```sh
docker compose -f mcp/docker-compose.yml up -d
```

This is a separate Compose project named `conference-mcp`. It joins the main stack's Docker network,
so it can reach the router, the four services and Hive by their service names.
To stop it, run `docker compose -f mcp/docker-compose.yml down`.

## The servers

| MCP server | URL (Streamable HTTP) | Tools |
|---|---|---|
| GraphQL, through the router | http://localhost:5100/mcp | `introspect`, `search`, `validate`, `execute` |
| Speakers REST API | http://localhost:5101/mcp | `api_speakers`, `api_speakers_id` |
| Sessions REST API | http://localhost:5102/mcp | `api_sessions`, `api_sessions_id` |
| Rooms REST API | http://localhost:5103/mcp | `api_rooms`, `api_rooms_id` |
| Feedback REST API | http://localhost:5104/mcp | `api_reviews`, `api_sessions_id_rating-summary`, `api_speakers_id_rating-summary` |

### GraphQL

The GraphQL server is the [Apollo MCP Server](https://www.apollographql.com/docs/apollo-mcp-server).
[`graphql.yaml`](graphql.yaml) configures it. It has no predefined operations. Instead, it gives the agent
four tools to explore the schema and write its own queries:

| Tool | What it does |
|---|---|
| `introspect` | Returns a type from the schema, with its fields and their descriptions |
| `search` | Finds types that match search terms |
| `validate` | Checks a query against the schema without running it |
| `execute` | Runs a query through the Apollo Router |

The agent learns what each field means from the descriptions in the subgraph schema files.
For example, `introspect` on `Session` explains that `averageRating` runs from 1.0 to 5.0
and is null when a session has no reviews yet.

The server needs the schema as a file. Before it starts, the `graphql-schema` container downloads
the current public schema from Hive's artifact endpoint (`/sdl`) into a shared volume.
If you publish a schema change to Hive, run `docker compose -f mcp/docker-compose.yml up -d --force-recreate`
to download the new schema.

### REST

Each REST server is [`evilfreelancer/openapi-to-mcp`](https://github.com/EvilFreelancer/openapi-to-mcp).
It reads one service's OpenAPI spec when it starts and creates one tool per endpoint.

- The tool name comes from the URL path. For example, `GET /api/sessions/{id}` becomes `api_sessions_id`.
- The tool description comes from the endpoint summary in the spec.
- The spec's own description becomes the server's instructions to the agent.

The image is only published for amd64, so on Apple Silicon it runs under emulation.

## Try a server by hand

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

1. Run `npx @modelcontextprotocol/inspector`.
2. Choose the **Streamable HTTP** transport.
3. Enter one of the URLs above and connect.
