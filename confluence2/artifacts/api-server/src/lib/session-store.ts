import { and, eq, gt, sql } from "drizzle-orm";
import { getDb, sessions, users } from "@workspace/db";
import type { AppUser, SessionData } from "./auth.js";
import { SESSION_TTL_MS } from "./auth.js";

export async function upsertUser(user: AppUser) {
  const db = getDb();
  const now = new Date();
  await db
    .insert(users)
    .values({
      id: user.id,
      email: user.email ?? null,
      firstName: user.firstName ?? null,
      lastName: user.lastName ?? null,
      profileImageUrl: user.profileImageUrl ?? null,
      createdAt: now,
      updatedAt: now,
    })
    .onConflictDoUpdate({
      target: users.id,
      set: {
        email: user.email ?? null,
        firstName: user.firstName ?? null,
        lastName: user.lastName ?? null,
        profileImageUrl: user.profileImageUrl ?? null,
        updatedAt: now,
      },
    });
}

export async function createSession(sid: string, data: SessionData) {
  const db = getDb();
  await upsertUser(data.user);
  await db.insert(sessions).values({
    sid,
    sess: data,
    expire: new Date(Date.now() + SESSION_TTL_MS),
  });
}

export async function updateSession(sid: string, data: SessionData) {
  const db = getDb();
  await db
    .update(sessions)
    .set({
      sess: data,
      expire: new Date(Date.now() + SESSION_TTL_MS),
    })
    .where(eq(sessions.sid, sid));
}

export async function getSession(sid: string): Promise<SessionData | null> {
  const db = getDb();
  const rows = await db
    .select()
    .from(sessions)
    .where(and(gt(sessions.expire, new Date()), eq(sessions.sid, sid)))
    .limit(1);

  const row = rows[0];
  if (!row) return null;
  return row.sess as SessionData;
}

export async function deleteSession(sid: string) {
  const db = getDb();
  await db.delete(sessions).where(eq(sessions.sid, sid));
}

export async function cleanupExpiredSessions() {
  const db = getDb();
  await db.delete(sessions).where(sql`${sessions.expire} <= NOW()`);
}
