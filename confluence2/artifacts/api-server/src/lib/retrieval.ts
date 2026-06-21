import { sql } from "drizzle-orm";
import { getDb } from "@workspace/db";

export type RetrievedPage = {
  id: number;
  title: string;
  content: string;
  domain: string;
  project: string;
  sourceType: string;
};

const STOP_WORDS = new Set([
  "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
  "by", "from", "is", "are", "was", "were", "be", "been", "being", "have", "has",
  "had", "do", "does", "did", "will", "would", "could", "should", "may", "might",
  "what", "which", "who", "whom", "this", "that", "these", "those", "how", "when",
  "where", "why", "can", "i", "me", "my", "we", "our", "you", "your", "it", "its",
]);

type RetrieveOptions = {
  question: string;
  domain?: string;
  project?: string;
  limit?: number;
};

function buildFilterClause(domain?: string, project?: string) {
  const clauses: ReturnType<typeof sql>[] = [];
  if (domain) clauses.push(sql`domain = ${domain}`);
  if (project) clauses.push(sql`project = ${project}`);
  if (!clauses.length) return sql`TRUE`;
  return sql.join(clauses, sql` AND `);
}

function keywordTerms(question: string): string[] {
  return question
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((term) => term.length > 2 && !STOP_WORDS.has(term));
}

export async function retrieveRelevantPages(
  options: RetrieveOptions,
): Promise<RetrievedPage[]> {
  const db = getDb();
  const limit = options.limit ?? 6;
  const filter = buildFilterClause(options.domain, options.project);

  const ftsRows = await db.execute<RetrievedPage>(sql`
    SELECT
      id,
      title,
      content,
      domain,
      project,
      source_type AS "sourceType"
    FROM pages
    WHERE ${filter}
      AND to_tsvector('english', title || ' ' || content) @@ (
        replace(
          websearch_to_tsquery('english', ${options.question})::text,
          ' & ',
          ' | '
        )::tsquery
      )
    ORDER BY ts_rank(
      to_tsvector('english', title || ' ' || content),
      replace(
        websearch_to_tsquery('english', ${options.question})::text,
        ' & ',
        ' | '
      )::tsquery
    ) DESC
    LIMIT ${limit}
  `);

  if (ftsRows.length > 0) {
    return ftsRows;
  }

  const terms = keywordTerms(options.question);
  if (!terms.length) {
    return [];
  }

  const keywordClauses = terms.map(
    (term) => sql`(title ILIKE ${"%" + term + "%"} OR content ILIKE ${"%" + term + "%"})`,
  );

  const keywordRows = await db.execute<RetrievedPage>(sql`
    SELECT
      id,
      title,
      content,
      domain,
      project,
      source_type AS "sourceType"
    FROM pages
    WHERE ${filter}
      AND (${sql.join(keywordClauses, sql` OR `)})
    ORDER BY updated_at DESC
    LIMIT ${limit}
  `);

  return keywordRows;
}
