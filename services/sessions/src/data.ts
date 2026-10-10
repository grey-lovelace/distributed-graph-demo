// Loads the sessions from data/sessions.json at startup and keeps them in memory.
// The GraphQL resolvers and the REST handlers both read from this file.

export type Session = {
  id: string;
  title: string;
  abstract: string;
  track: string;
  level: string;
  startsAt: string;
  endsAt: string;
  speakerIds: string[];
  roomId: string;
};

export type SessionFilters = {
  day?: string | null;
  track?: string | null;
  startsAfter?: string | null;
  speakerId?: string | null;
  roomId?: string | null;
};

const allSessions: Session[] = await Bun.file("data/sessions.json").json();
allSessions.sort((a, b) => a.startsAt.localeCompare(b.startsAt));

export function findSessions(filters: SessionFilters): Session[] {
  return allSessions.filter((session) => {
    if (filters.day && !session.startsAt.startsWith(filters.day)) return false;
    if (filters.track && session.track !== filters.track) return false;
    if (filters.startsAfter && new Date(session.startsAt) < new Date(filters.startsAfter)) return false;
    if (filters.speakerId && !session.speakerIds.includes(filters.speakerId)) return false;
    if (filters.roomId && session.roomId !== filters.roomId) return false;
    return true;
  });
}

export function findSessionById(id: string): Session | undefined {
  return allSessions.find((session) => session.id === id);
}
