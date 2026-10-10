// Resolves the fields in schema.graphql.
import type { GraphQLResolverMap } from "@apollo/subgraph";
import { findSessionById, findSessions, type Session, type SessionFilters } from "./data";

export const resolvers: GraphQLResolverMap = {
  Query: {
    sessions: (_parent, filters: SessionFilters) => findSessions(filters),
    session: (_parent, { id }: { id: string }) => findSessionById(id),
  },

  Session: {
    // This is the reference resolver for the Session entity.
    // The router sends a session id from another subgraph, and this function returns the full session.
    __resolveReference: ({ id }: { id: string }) => findSessionById(id),

    // This service stores only speaker IDs. Each returned object is an entity reference.
    // The router uses the id to fetch the rest of each speaker from the Speakers subgraph.
    speakers: (session: Session) => session.speakerIds.map((id) => ({ id })),

    // This service stores only the room ID. The router fetches the room from the Rooms subgraph.
    room: (session: Session) => ({ id: session.roomId }),
  },

  // These resolvers add the sessions field to the Speaker and Room entities.
  // The router passes in a reference that contains only the id.
  Speaker: {
    sessions: ({ id }: { id: string }) => findSessions({ speakerId: id }),
  },

  Room: {
    sessions: ({ id }: { id: string }) => findSessions({ roomId: id }),
  },
};
