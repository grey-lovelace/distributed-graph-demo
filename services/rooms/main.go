package main

import (
	"log"
	"net/http"

	"github.com/99designs/gqlgen/graphql/handler"
	"github.com/99designs/gqlgen/graphql/handler/extension"
	"github.com/99designs/gqlgen/graphql/handler/transport"
	"github.com/99designs/gqlgen/graphql/playground"

	"demo/rooms/graph"
	"demo/rooms/store"
)

func main() {
	rooms, err := store.Load("data/rooms.json")
	if err != nil {
		log.Fatalf("could not load rooms: %v", err)
	}

	mux := http.NewServeMux()

	// GraphQL subgraph
	schema := graph.NewExecutableSchema(graph.Config{Resolvers: &graph.Resolver{Store: rooms}})
	graphqlServer := handler.New(schema)
	graphqlServer.AddTransport(transport.POST{})
	graphqlServer.Use(extension.Introspection{})
	mux.Handle("POST /graphql", graphqlServer)
	mux.Handle("GET /graphql", playground.Handler("Rooms subgraph", "/graphql"))

	// REST API and its OpenAPI docs
	registerRestRoutes(mux, rooms)
	if err := registerDocsRoutes(mux); err != nil {
		log.Fatalf("could not load openapi.yaml: %v", err)
	}

	log.Println("Rooms service listening on http://localhost:4003")
	log.Fatal(http.ListenAndServe(":4003", mux))
}
