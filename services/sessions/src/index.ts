import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@as-integrations/express5";
import { buildSubgraphSchema } from "@apollo/subgraph";
import express from "express";
import { parse } from "graphql";
import { docsRouter } from "./docs";
import { resolvers } from "./resolvers";
import { restRouter } from "./rest";

// buildSubgraphSchema turns the schema into a Federation subgraph.
// It adds the _service and _entities fields that the router calls.
const typeDefs = parse(await Bun.file("schema.graphql").text());
const server = new ApolloServer({ schema: buildSubgraphSchema([{ typeDefs, resolvers }]) });
await server.start();

const app = express();

// GraphQL subgraph
app.use("/graphql", express.json(), expressMiddleware(server));

// REST API and its OpenAPI docs
app.use(restRouter);
app.use(docsRouter);

app.listen(4002, () => {
  console.log("Sessions service listening on http://localhost:4002");
});
