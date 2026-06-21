import crypto from "node:crypto";
import type { Request } from "express";

export type AppUser = {
  id: string;
  email?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  profileImageUrl?: string | null;
};

export type SessionData = {
  user: AppUser;
  accessToken?: string;
  refreshToken?: string;
  idToken?: string;
  expiresAt?: number;
};

export const SESSION_COOKIE = "sid";
export const SESSION_TTL_MS = 7 * 24 * 60 * 60 * 1000;

export function isDevAuthBypassEnabled(): boolean {
  if (process.env.DEV_AUTH_BYPASS === "true") return true;
  return !process.env.REPL_ID;
}

export function createSessionId(): string {
  return crypto.randomBytes(32).toString("hex");
}

export function getSessionIdFromRequest(req: Request): string | null {
  const bearer = req.headers.authorization;
  if (bearer?.startsWith("Bearer ")) {
    return bearer.slice("Bearer ".length).trim() || null;
  }
  const cookieSid = req.cookies?.[SESSION_COOKIE];
  return typeof cookieSid === "string" ? cookieSid : null;
}

export function getDevUser(): AppUser {
  return {
    id: "dev-user",
    email: "dev@localhost",
    firstName: "Dev",
    lastName: "User",
    profileImageUrl: null,
  };
}

export function getWebOrigin(): string {
  return process.env.WEB_ORIGIN ?? "http://localhost:5173";
}

export function getApiBaseUrl(req: Request): string {
  const proto = req.get("x-forwarded-proto") ?? req.protocol;
  const host = req.get("x-forwarded-host") ?? req.get("host");
  return `${proto}://${host}`;
}

export function getCallbackUrl(req: Request): string {
  return `${getApiBaseUrl(req)}/api/callback`;
}

export function getAllowedDomains(): string[] {
  return (process.env.REPLIT_DOMAINS ?? "localhost:5000")
    .split(",")
    .map((d) => d.trim())
    .filter(Boolean);
}
