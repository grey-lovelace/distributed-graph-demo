// Serves the sessions as a REST API under /api/sessions.
import { Router } from "express";
import { findSessionById, findSessions } from "./data";

export const restRouter = Router();

restRouter.get("/api/sessions", (req, res) => {
  const sessions = findSessions({
    day: req.query.day as string | undefined,
    track: req.query.track as string | undefined,
    startsAfter: req.query.startsAfter as string | undefined,
    speakerId: req.query.speakerId as string | undefined,
    roomId: req.query.roomId as string | undefined,
  });
  res.json(sessions);
});

restRouter.get("/api/sessions/:id", (req, res) => {
  const session = findSessionById(req.params.id);
  if (!session) {
    res.status(404).json({ error: `Session not found: ${req.params.id}` });
    return;
  }
  res.json(session);
});
