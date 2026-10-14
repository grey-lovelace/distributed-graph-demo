# Conference Platform: A Federated Graph demo

This repository is the demo from the talk **"The Apollo Supergraph: Unifying APIs for AI and the Enterprise."**
You can run the whole thing on your own machine and try everything from the talk yourself.

The demo is a conference platform built from four independent services. Each service is written in a
different language and owns its own data. Each one exposes a GraphQL subgraph and a REST API over
the same data, so you can compare the two styles side by side.

The four subgraphs publish their schemas to [Hive](https://the-guild.dev/graphql/hive), an open source
schema registry that runs locally in Docker. Hive composes the schemas into one supergraph.
The Apollo Router downloads the supergraph from Hive and serves a single graph on port 4000.

## The slides

The slides from the talk are in the [`slides/`](slides) folder. They are an HTML deck built with
[reveal.js](https://revealjs.com), so the animations work in any modern browser.

- **View them online** at https://grey-lovelace.github.io/distributed-graph-demo/.
- **Open them locally:** open `slides/index.html` in a browser. Everything the deck needs is in the
  folder, so it works offline with nothing to install.

While the deck is open, use the arrow keys to move between slides. Press **S** for the speaker notes,
**Esc** to see every slide at once, and **P** to print the deck or save it as a PDF.

## What you need

- Docker with Docker Compose 2.20 or later.
- About 3 GB of free memory for Docker.
- An internet connection for the first build, which downloads the images and dependencies.

You do not need Java, Node.js, Go or Python on your machine. Everything builds and runs in containers.

## Quick start

```sh
docker compose up --build
```

The first run takes a few minutes, because Docker downloads the Hive images and Gradle downloads the
Java dependencies. Later starts take about 45 seconds.

When the stack is up, try these:

1. Open **Apollo Sandbox** at http://localhost:4000 and run one of the [example queries](#example-graphql-queries).
2. Open the **Hive web app** at http://localhost:8080 and sign in:
   - Email: `demo@conference.local`
   - Password: `Conference-demo-2026!`

   Then open the **conference** organization, the **conference-platform** project and the **production** target.
3. Open any service's **Swagger UI**, for example http://localhost:4002/docs, to try its REST API.

To stop everything, run `docker compose down`. To also delete Hive's data and start fresh next time,
run `docker compose down -v`.

## Start it one step at a time

`docker compose up --build` starts everything at once. If you want to watch the graph grow piece by
piece, as in the talk, start each part with its own command instead. Run `docker compose build` once
first, so that no step has to wait for a build.

| Step | Command | What happens |
|---|---|---|
| 1. Start Hive | `docker compose up -d hive-setup` | Starts all of Hive and runs the setup. Open http://localhost:8080 to see the empty project. |
| 2. Start a subgraph | `docker compose up -d speakers` | Starts the Speakers service. Hive does not know about it yet. |
| 3. Publish its schema | `docker compose run --rm --no-deps publish-speakers` | Publishes the schema file and prints a link to the new version in Hive. |
| 4. Start the router | `docker compose up -d router` | Downloads the supergraph from Hive. The graph has only the Speakers fields. |
| 5. Add each other subgraph | `docker compose up -d sessions`<br>`docker compose run --rm --no-deps publish-sessions` | The router picks up the new supergraph within 10 seconds, without a restart. Repeat for `rooms` and `feedback`. |

Start the router only after at least one schema is published. Before that, Hive has no supergraph,
so the router exits. The `--no-deps` flag stops Compose from running `hive-setup` again, which it
sometimes does for `run`.

Things to notice along the way:

- **Publishing does not need the subgraph to be running.** `hive schema:publish` sends the schema file
  and the routing URL to Hive. Hive never calls the subgraph. Only the router does.
- **A field exists only after its subgraph publishes.** For example, before Rooms publishes,
  a query for `Session.room { name }` fails validation with `Cannot query field "name" on type "Room"`.
- **A published subgraph that is not running fails the query.** If you publish Sessions before you start it,
  a query that needs Sessions fails with `GATEWAY_TIMEOUT` after the router's 30-second timeout.
  The router does not return partial data in this case.

## How it works

```
                       1. publish schema
   speakers  ─┐       (hive schema:publish)       ┌────────────────────────────┐
   sessions  ─┼──────────────────────────────────▶│  Hive schema registry      │
   rooms     ─┤                                   │  web app :8080, API :8082  │
   feedback  ─┘                                   │  2. composes the supergraph│
       ▲                                          └─────────────┬──────────────┘
       │                                                        │ 3. router downloads the
       │ 5. router calls each subgraph                          │    supergraph every 10 s
       │                                          ┌─────────────▼──────────────┐
       └──────────────────────────────────────────│  Apollo Router  :4000      │◀── clients, AI agents
                                                  │  4. sends usage reports    │
                                                  │     back to Hive           │
                                                  └────────────────────────────┘

   speakers :4001  Java, Spring       sessions :4002  TypeScript, Bun
   rooms    :4003  Go, gqlgen         feedback :4004  Python, FastAPI
```

When you run `docker compose up --build`, these steps happen in order:

1. Docker starts Hive: its database, storage, message broker, API and web app.
2. When all of Hive is healthy, `hive-setup` runs once. It creates a demo user, an organization,
   a Federation project and two access tokens, and then it exits. See [`hive/setup.py`](hive/setup.py).
3. Docker builds and starts the four services.
4. Each `publish-*` container publishes one service's schema file to Hive, and then it exits.
   Hive composes the supergraph after each publish.
5. The Apollo Router downloads the supergraph from Hive. If the router starts before the first publish,
   it exits, and Docker restarts it until Hive has a supergraph.

### Compared with Apollo GraphOS

If you have used Apollo GraphOS, the workflow is the same. The difference is that the registry runs
on your machine instead of in the cloud.

| Step | With Apollo GraphOS | In this project |
|---|---|---|
| A subgraph publishes its schema | `rover subgraph publish` | `hive schema:publish` |
| A pull request checks its schema | `rover subgraph check` | `hive schema:check` |
| The registry composes the supergraph | GraphOS, in the cloud | Hive, in Docker |
| The router gets the supergraph | Apollo Uplink, with `APOLLO_KEY` | Hive's artifact endpoint, with a CDN access token |
| The router reports usage | To GraphOS | To Hive |
| You look at schemas, history and usage | Apollo Studio | The Hive web app at http://localhost:8080 |

### The four subgraphs

| Folder | Subgraph | Stack | Schema file | Owns | Adds fields to other entities |
|---|---|---|---|---|---|
| `services/speakers/` | `speakers` | Java 21, Spring Boot 3.5, Spring for GraphQL, `federation-jvm` | [`src/main/resources/graphql/schema.graphqls`](services/speakers/src/main/resources/graphql/schema.graphqls) | `Speaker` | none |
| `services/sessions/` | `sessions` | TypeScript, Bun, Apollo Server 5, `@apollo/subgraph` | [`schema.graphql`](services/sessions/schema.graphql) | `Session` | `Speaker.sessions`, `Room.sessions` |
| `services/rooms/` | `rooms` | Go, gqlgen, `net/http` | [`graph/schema.graphqls`](services/rooms/graph/schema.graphqls) | `Room` | none |
| `services/feedback/` | `feedback` | Python 3.13, FastAPI, Ariadne, uv | [`schema.graphql`](services/feedback/schema.graphql) | `Review` | `Session.reviews`, `Session.averageRating`, `Session.reviewCount`, `Speaker.averageRating` |

Every subgraph is schema-first: the schema file is the source of truth, and the resolvers implement it.
Each schema file has a description on every type and field, so that people and AI agents can read
what each field means.

Services refer to each other only by ID. For example, the Sessions service stores a list of speaker
IDs and one room ID for each session. It never stores a speaker's name or a room's capacity.
The router fetches those fields from the service that owns them.

Each service follows the same layout, so you can compare the four languages file by file:

| Concern | `speakers` (Java) | `sessions` (TypeScript) | `rooms` (Go) | `feedback` (Python) |
|---|---|---|---|---|
| Schema | `schema.graphqls` | `schema.graphql` | `graph/schema.graphqls` | `schema.graphql` |
| GraphQL resolvers | `SpeakerGraphQLController.java` | `src/resolvers.ts` | `graph/*.resolvers.go` | `resolvers.py` |
| REST handlers | `SpeakerRestController.java` | `src/rest.ts` | `rest.go` | `rest.py` |
| Data access | `SpeakerData.java` | `src/data.ts` | `store/store.go` | `data.py` |
| Data file (in the top-level `data/` folder) | `speakers.json` | `sessions.json` | `rooms.json` | `reviews.json` |
| OpenAPI | generated by springdoc | hand-written `openapi.yaml` | hand-written `openapi.yaml` | generated by FastAPI |

The code has short comments wherever a federation concept appears, such as `@key`, a reference resolver,
or a field that one subgraph adds to another subgraph's entity.

## Example GraphQL queries

Open http://localhost:4000 in a browser to use Apollo Sandbox, and paste in any query below.
The [`queries/`](queries) folder holds these operations and a few more as `.graphql` files.

### 1. A speaker, their sessions, each session's room, and each session's rating

This query crosses all four subgraphs. The comments show which subgraph provides each field.

```graphql
query SpeakerProfile {
  speaker(id: "speaker-20") {
    name
    company
    companyType
    averageRating          # from feedback
    sessions {             # from sessions
      title
      startsAt
      averageRating        # from feedback
      reviewCount          # from feedback
      room {               # from rooms
        name
        capacity
      }
    }
  }
}
```

### 2. "Which top-rated sessions this afternoon are in the biggest room, and who is giving them?"

This is the question that the AI agent answers in the talk. The conference runs on **2026-11-12**
and **2026-11-13** in London, so all times are in UTC. Treat 2026-11-12 as "today" and 12:00 as the
start of the afternoon.

```graphql
query AfternoonSessions {
  sessions(day: "2026-11-12", startsAfter: "2026-11-12T12:00:00Z") {
    title
    startsAt
    averageRating
    room {
      name
      capacity
    }
    speakers {
      name
      company
      companyType
    }
  }
}
```

The Main Hall (capacity 800) is the biggest room. It holds three sessions that afternoon,
with average ratings of 4.33, 2.4, and 4.14. Each of the three has a speaker from a consultancy.

### 3. Every room and its schedule

```graphql
query RoomSchedule {
  rooms {
    name
    capacity
    sessions {
      title
      startsAt
      averageRating
    }
  }
}
```

### See the query plan

The query plan shows which subgraphs the router calls, and in what order.

- **In Sandbox:** run a query, then open the **Query Plan** panel next to the response.
- **With curl:** send the `Apollo-Expose-Query-Plan: true` header. The plan is in `extensions.apolloQueryPlan`.

```sh
curl -s http://localhost:4000/ \
  -H 'content-type: application/json' \
  -H 'Apollo-Expose-Query-Plan: true' \
  -d '{"query":"{ speaker(id: \"speaker-20\") { name sessions { title averageRating room { name } } } }"}'
```

## The same questions with REST

Every service also has a REST API over the same data. The REST APIs return IDs for related data,
not embedded objects. So a client, or an AI agent, has to make many calls and join the results itself.
Compare these call sequences with the single GraphQL queries above.

### Query 1 with REST: a speaker, their sessions, rooms, and ratings

```sh
# 1. Get the speaker.
curl http://localhost:4001/api/speakers/speaker-20

# 2. Get the speaker's sessions. Each session has a roomId.
curl 'http://localhost:4002/api/sessions?speakerId=speaker-20'

# 3. Get each room. Repeat for every roomId from step 2.
curl http://localhost:4003/api/rooms/room-01
curl http://localhost:4003/api/rooms/room-04

# 4. Get each session's rating. Repeat for every session from step 2.
curl http://localhost:4004/api/sessions/session-09/rating-summary
curl http://localhost:4004/api/sessions/session-11/rating-summary
curl http://localhost:4004/api/sessions/session-17/rating-summary

# 5. Get the speaker's own rating.
curl http://localhost:4004/api/speakers/speaker-20/rating-summary
```

That is 8 calls to 4 services, compared with 1 GraphQL call to the router.

### Query 2 with REST: the afternoon sessions in the biggest room

```sh
# 1. Get all rooms. The list is sorted by capacity, so the first room is the biggest: room-01.
curl http://localhost:4003/api/rooms

# 2. Get the afternoon sessions in that room.
curl 'http://localhost:4002/api/sessions?day=2026-11-12&startsAfter=2026-11-12T12:00:00Z&roomId=room-01'

# 3. Get the rating of each session from step 2.
curl http://localhost:4004/api/sessions/session-09/rating-summary
curl http://localhost:4004/api/sessions/session-13/rating-summary
curl http://localhost:4004/api/sessions/session-17/rating-summary

# 4. Get each speaker from step 2.
curl http://localhost:4001/api/speakers/speaker-19
curl http://localhost:4001/api/speakers/speaker-20
curl http://localhost:4001/api/speakers/speaker-01
curl http://localhost:4001/api/speakers/speaker-06
curl http://localhost:4001/api/speakers/speaker-21
```

That is 10 calls to 4 services. After that, the client must sort the sessions by rating and match
each speaker ID to a speaker.

### All REST endpoints

| Service | Endpoint | Returns |
|---|---|---|
| speakers | `GET /api/speakers` | All speakers, sorted by name |
| speakers | `GET /api/speakers/{id}` | One speaker |
| sessions | `GET /api/sessions?day=&track=&startsAfter=&speakerId=&roomId=` | Sessions sorted by start time. Every filter is optional. |
| sessions | `GET /api/sessions/{id}` | One session, with `speakerIds` and `roomId` |
| rooms | `GET /api/rooms` | All rooms, from largest to smallest |
| rooms | `GET /api/rooms/{id}` | One room |
| feedback | `GET /api/reviews?sessionId=&speakerId=` | Reviews sorted by submission time. Both filters are optional. |
| feedback | `GET /api/sessions/{id}/rating-summary` | `averageRating` and `reviewCount` for one session |
| feedback | `GET /api/speakers/{id}/rating-summary` | `averageRating` and `reviewCount` for one speaker |

An unknown ID returns HTTP 404 with a JSON body that contains an error message.

## Try the schema registry workflow

You can change a schema and watch it go through Hive to the router, like a change in a real team's
CI pipeline. Run these commands from the repository root while the stack is up.
`--no-deps` stops Compose from running `hive-setup` again. Running it again does no harm,
but it takes a few seconds and creates new tokens.

1. Edit a schema file, for example `services/sessions/schema.graphql`.
2. Check the change against the published schemas and recent usage:

   ```sh
   docker compose run --rm --no-deps publish-sessions check sessions
   ```

   If you remove a field, such as `Session.level`, the check fails and lists the breaking change.
   It also prints a link to the check in the Hive web app.

3. Publish the change:

   ```sh
   docker compose run --rm --no-deps publish-sessions publish sessions
   ```

   Hive composes a new supergraph. The router downloads it within 10 seconds and logs
   `reload complete` without a restart. The new version appears in the **History** tab of the Hive web app.

   If the change does not compose with the other subgraphs, the publish fails and Hive stores nothing.
   For example, add `name: String!` to the `Room` type in `services/sessions/schema.graphql`.
   The Rooms subgraph owns `Room.name`, so the publish fails with
   `Non-shareable field Room.name is resolved from multiple subgraphs`.

If you change a resolver as well as the schema, rebuild the service first:
`docker compose up --build -d sessions`.

### Explore the Hive web app

- **Schema** and **Explorer** show the composed supergraph and which subgraph owns each field.
- **History** shows every publish, with the author (for example, "sessions team") and the changes.
- **Checks** shows each schema check, with its breaking changes.
- **Insights** shows the operations that clients sent through the router, with their latency and the fields they use.
  The router sends these usage reports to Hive about every 5 seconds, so run a few queries first.

## MCP servers for AI agents

The [`mcp/`](mcp) folder holds MCP servers that give an AI agent access to the same data,
either through the graph or through the REST APIs. Start the main stack first, then run:

```sh
docker compose -f mcp/docker-compose.yml up -d
```

See [`mcp/README.md`](mcp/README.md) for the servers, their URLs and their tools.

## An AI agent that uses them

The [`ai/`](ai) folder holds a Jupyter notebook that builds two LangChain agents. One uses the REST
MCP servers and the other uses the GraphQL MCP server. The notebook asks both the same questions and compares
their tool calls, tokens and time. See [`ai/README.md`](ai/README.md) to run it.

## Ports and URLs

| Service | GraphQL | REST | OpenAPI spec | Swagger UI |
|---|---|---|---|---|
| **Router** | http://localhost:4000 (opens Apollo Sandbox in a browser) | | | |
| **Hive web app** | http://localhost:8080 | | | |
| **Hive API** | http://localhost:8082/graphql | | | |
| `speakers` | http://localhost:4001/graphql | http://localhost:4001/api/speakers | http://localhost:4001/openapi.json | http://localhost:4001/docs |
| `sessions` | http://localhost:4002/graphql | http://localhost:4002/api/sessions | http://localhost:4002/openapi.json | http://localhost:4002/docs |
| `rooms` | http://localhost:4003/graphql | http://localhost:4003/api/rooms | http://localhost:4003/openapi.json | http://localhost:4003/docs |
| `feedback` | http://localhost:4004/graphql | http://localhost:4004/api/reviews | http://localhost:4004/openapi.json | http://localhost:4004/docs |

The router also has a health endpoint at http://localhost:8088/health inside the Docker network.

## Data

All the data lives in the top-level [`data/`](data) folder. Each service loads one JSON file
into memory at startup. There is no database.

| File | Service | Records |
|---|---|---|
| `data/speakers.json` | speakers | 90 speakers from consultancies, product companies, enterprises, and non-profits |
| `data/rooms.json` | rooms | 18 rooms, with capacities from 30 to 800 |
| `data/sessions.json` | sessions | 120 sessions over two days in five tracks |
| `data/reviews.json` | feedback | 1,153 reviews |

`docker-compose.yml` mounts each file into its own service container at `/app/data/<file>.json`.
A service receives only its own file, so no service can read another service's data.

The IDs line up across the files. Every speaker ID and room ID in `sessions.json` exists in the
other files, and every session ID and speaker ID in `reviews.json` exists too.

One session, `session-40`, has no reviews yet, so its `averageRating` is `null`.

## Hive and router files

| File | What it does |
|---|---|
| [`hive/docker-compose.yml`](hive/docker-compose.yml) | Runs Hive. It is Hive's official Compose file for release 12.1.0 with four small changes, which the file header lists. A comment above each service explains what that service does. The root `docker-compose.yml` includes this file. |
| [`hive/hive.env`](hive/hive.env) | The Hive settings and secrets. They are for a local demo only. Never reuse them. |
| [`hive/setup.py`](hive/setup.py) | Creates the demo user, organization, project and access tokens through the Hive API. |
| [`hive/schema-registry.sh`](hive/schema-registry.sh) | Publishes or checks one subgraph schema with the Hive CLI. |
| [`router/router.yaml`](router/router.yaml) | Configures the router. It turns on introspection, Sandbox, query plans and Hive usage reporting. |

`hive-setup` writes the access tokens to a shared Docker volume. The publish containers and the
router read them from there. The setup runs on every full start and creates new tokens each time.

The whole stack has about 20 containers and uses about 2.7 GB of memory. Most of that is Hive,
and ClickHouse alone uses about 840 MB.

### Regenerating the Go code

The gqlgen output in `services/rooms/graph/` is committed. If you change `services/rooms/graph/schema.graphqls`,
regenerate it from the `services/rooms/` folder. This step needs Go installed on your machine.

```sh
go tool gqlgen generate
```