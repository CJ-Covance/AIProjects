import type { NextFunction, Request, Response } from "express";
import {
  createSessionId,
  getSessionIdFromRequest,
  SESSION_COOKIE,
  type SessionData,
} from "../lib/auth.js";
import { refreshSessionTokens } from "../lib/oidc.js";
import { getSession, updateSession } from "../lib/session-store.js";

declare global {
  namespace Express {
    interface Request {
      session?: SessionData;
      sessionId?: string;
    }
  }
}

export async function authMiddleware(req: Request, res: Response, next: NextFunction) {
  try {
    const sid = getSessionIdFromRequest(req);
    if (!sid) {
      return next();
    }

    const session = await getSession(sid);
    if (!session) {
      res.clearCookie(SESSION_COOKIE);
      return next();
    }

    try {
      const refreshed = await refreshSessionTokens(session);
      if (refreshed !== session) {
        await updateSession(sid, refreshed);
      }
      req.session = refreshed;
      req.sessionId = sid;
    } catch {
      res.clearCookie(SESSION_COOKIE);
      return next();
    }

    return next();
  } catch (error) {
    return next(error);
  }
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  if (!req.session?.user) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  return next();
}

export function setSessionCookie(res: Response, sid: string) {
  res.cookie(SESSION_COOKIE, sid, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });
}

export async function issueSession(res: Response, session: SessionData) {
  const sid = createSessionId();
  const { createSession } = await import("../lib/session-store.js");
  await createSession(sid, session);
  setSessionCookie(res, sid);
  return sid;
}
