import { and, desc, eq, ilike, or, sql } from "drizzle-orm";
import { Router } from "express";
import { z } from "zod";
import { getDb, pages, questions } from "@workspace/db";
import { requireAuth } from "../middlewares/authMiddleware.js";

const router = Router();

const createPageSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
  domain: z.string().min(1),
  project: z.string().min(1),
});

function mapPage(row: typeof pages.$inferSelect) {
  return {
    id: row.id,
    title: row.title,
    content: row.content,
    domain: row.domain,
    project: row.project,
    sourceType: row.sourceType,
    createdAt: row.createdAt.toISOString(),
    updatedAt: row.updatedAt.toISOString(),
  };
}

router.get("/pages", requireAuth, async (req, res, next) => {
  try {
    const db = getDb();
    const domain = typeof req.query.domain === "string" ? req.query.domain : undefined;
    const project = typeof req.query.project === "string" ? req.query.project : undefined;
    const search = typeof req.query.search === "string" ? req.query.search : undefined;

    const filters = [];
    if (domain) filters.push(eq(pages.domain, domain));
    if (project) filters.push(eq(pages.project, project));
    if (search) {
      filters.push(
        or(
          ilike(pages.title, `%${search}%`),
          ilike(pages.content, `%${search}%`),
          ilike(pages.domain, `%${search}%`),
          ilike(pages.project, `%${search}%`),
        )!,
      );
    }

    const rows = await db
      .select()
      .from(pages)
      .where(filters.length ? and(...filters) : undefined)
      .orderBy(desc(pages.updatedAt));

    res.json(rows.map(mapPage));
  } catch (error) {
    next(error);
  }
});

router.post("/pages", requireAuth, async (req, res, next) => {
  try {
    const input = createPageSchema.parse(req.body);
    const db = getDb();
    const now = new Date();
    const [row] = await db
      .insert(pages)
      .values({
        title: input.title,
        content: input.content,
        domain: input.domain,
        project: input.project,
        sourceType: "manual",
        createdAt: now,
        updatedAt: now,
      })
      .returning();

    res.status(201).json(mapPage(row));
  } catch (error) {
    next(error);
  }
});

router.get("/pages/:id", requireAuth, async (req, res, next) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isFinite(id)) {
      return res.status(400).json({ error: "Invalid page id" });
    }

    const db = getDb();
    const [row] = await db.select().from(pages).where(eq(pages.id, id)).limit(1);
    if (!row) {
      return res.status(404).json({ error: "Page not found" });
    }
    return res.json(mapPage(row));
  } catch (error) {
    return next(error);
  }
});

router.delete("/pages/:id", requireAuth, async (req, res, next) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isFinite(id)) {
      return res.status(400).json({ error: "Invalid page id" });
    }

    const db = getDb();
    const deleted = await db.delete(pages).where(eq(pages.id, id)).returning({ id: pages.id });
    if (!deleted.length) {
      return res.status(404).json({ error: "Page not found" });
    }
    return res.status(204).send();
  } catch (error) {
    return next(error);
  }
});

router.get("/knowledge-stats", requireAuth, async (_req, res, next) => {
  try {
    const db = getDb();
    const [pageCount] = await db.select({ count: sql<number>`count(*)::int` }).from(pages);
    const [questionCount] = await db.select({ count: sql<number>`count(*)::int` }).from(questions);
    const topDomains = await db
      .select({
        domain: pages.domain,
        count: sql<number>`count(*)::int`,
      })
      .from(pages)
      .groupBy(pages.domain)
      .orderBy(sql`count(*) DESC`)
      .limit(5);

    res.json({
      totalPages: pageCount?.count ?? 0,
      totalQuestions: questionCount?.count ?? 0,
      topDomains,
    });
  } catch (error) {
    next(error);
  }
});

router.get("/workspaces", requireAuth, async (_req, res, next) => {
  try {
    const db = getDb();
    const rows = await db
      .select({
        domain: pages.domain,
        project: pages.project,
        pageCount: sql<number>`count(*)::int`,
      })
      .from(pages)
      .groupBy(pages.domain, pages.project)
      .orderBy(pages.domain, pages.project);

    res.json(rows);
  } catch (error) {
    next(error);
  }
});

export default router;
