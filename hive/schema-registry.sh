#!/bin/sh
# Publishes or checks one subgraph schema in the Hive schema registry.
#
# Usage:
#   schema-registry.sh publish <subgraph>
#   schema-registry.sh check <subgraph>
#
# <subgraph> is speakers, sessions, rooms or feedback.
# The tokens come from the file that hive/setup.py writes.
set -e
. /hive-tokens/hive.env

action="$1"
subgraph="$2"

# Each subgraph has a routing URL and a schema file.
# The router sends queries to the routing URL. The schema file is what gets published.
case "$subgraph" in
  speakers) url="http://speakers:4001/graphql"; schema="/services/speakers/src/main/resources/graphql/schema.graphqls" ;;
  sessions) url="http://sessions:4002/graphql"; schema="/services/sessions/schema.graphql" ;;
  rooms)    url="http://rooms:4003/graphql";    schema="/services/rooms/graph/schema.graphqls" ;;
  feedback) url="http://feedback:4004/graphql"; schema="/services/feedback/schema.graphql" ;;
  *) echo "Unknown subgraph: $subgraph. Use speakers, sessions, rooms or feedback." >&2; exit 1 ;;
esac

case "$action" in
  publish)
    # Hive stores the new schema version, composes the supergraph, and serves it to the router.
    # Without --fail-on-composition-error, Hive would store a schema that does not compose,
    # mark the version as not composable, and keep serving the last good supergraph.
    # With the flag, the publish fails instead, and Hive stores nothing.
    hive schema:publish \
      --fail-on-composition-error \
      --registry.endpoint "$HIVE_REGISTRY_ENDPOINT" \
      --registry.accessToken "$HIVE_TOKEN" \
      --target "$HIVE_TARGET_ID" \
      --service "$subgraph" \
      --url "$url" \
      --author "$subgraph team" \
      --commit "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      "$schema"
    ;;
  check)
    # Hive composes the schema with the other published subgraphs and reports breaking changes.
    # It does not store anything.
    hive schema:check \
      --registry.endpoint "$HIVE_REGISTRY_ENDPOINT" \
      --registry.accessToken "$HIVE_TOKEN" \
      --target "$HIVE_TARGET_ID" \
      --service "$subgraph" \
      "$schema"
    ;;
  *) echo "Unknown action: $action. Use publish or check." >&2; exit 1 ;;
esac
