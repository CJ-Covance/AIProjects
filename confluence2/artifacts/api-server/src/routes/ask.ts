import { desc } from "drizzle-orm";
import { Router } from "express";
import { z } from "zod";
import { getDb, questions } from "@workspace/db";
import { buildSnippet, generateAnswer } from "../lib/gemini.js";
import { retrieveRelevantPages } from "../lib/retrieval.js";
import { requireAuth } from "../middlewares/authMiddleware.js";

const router = Router();

const askSchema = z.object({
  question: z.string().min(1),
  domain: z.string().optional(),
  project: z.string().optional(),
});

router.post("/ask", requireAuth, async (req, res, next) => {
  try {
    const input = askSchema.parse(req.body);
    const retrieved = await retrieveRelevantPages({
      question: input.question,
      domain: input.domain,
      project: input.project,
      limit: 6,
    });

    const generated = await generateAnswer(input.question, retrieved);
    const retrievedIds = new Set(retrieved.map((page) => page.id));
    const validCitedIds = generated.citedPageIds.filter((id) => retrievedIds.has(id));

    const citations = validCitedIds
      .map((pageId) => retrieved.find((page) => page.id === pageId))
      .filter((page): page is NonNullable<typeof page> => Boolean(page))
      .map((page) => ({
        pageId: page.id,
        title: page.title,
        domain: page.domain,
        project: page.project,
        snippet: buildSnippet(page.content),
      }));

    const db = getDb();
    await db.insert(questions).values({
      question: input.question,
      answer: generated.answer,
      citationCount: citations.length,
    });

    res.json({
      question: input.question,
      answer: generated.answer,
      citations,
      sourcesConsidered: retrieved.length,
    });
  } catch (error) {
    next(error);
  }
});

router.get("/ask/history", requireAuth, async (req, res, next) => {
  try {
    const rawLimit = Number(req.query.limit ?? 20);
    const limit = Math.min(Math.max(Number.isFinite(rawLimit) ? rawLimit : 20, 1), 100);
    const db = getDb();
    const rows = await db
      .select()
      .from(questions)
      .orderBy(desc(questions.createdAt))
      .limit(limit);

    res.json(
      rows.map((row) => ({
        id: row.id,
        question: row.question,
        answer: row.answer,
        citationCount: row.citationCount,
        createdAt: row.createdAt.toISOString(),
      })),
    );
  } catch (error) {
    next(error);
  }
});

export default router;
