import { createGeminiClient, resolveGeminiConfigFromEnv } from "@workspace/integrations-gemini-ai";
import type { RetrievedPage } from "./retrieval.js";

export type GeneratedAnswer = {
  answer: string;
  citedPageIds: number[];
};

function buildPrompt(question: string, pages: RetrievedPage[]) {
  const sources = pages
    .map(
      (page) =>
        `[PAGE_ID:${page.id}] Title: ${page.title}\nDomain: ${page.domain}\nProject: ${page.project}\nContent:\n${page.content}`,
    )
    .join("\n\n---\n\n");

  return `You are a grounded enterprise knowledge assistant.

Answer the user's question using ONLY the source pages below.
If the sources do not contain enough information, say you could not find enough information in the knowledge base.
Return valid JSON with this exact shape:
{"answer":"...", "citedPageIds":[1,2]}

Rules:
- citedPageIds must only include page IDs from the provided sources.
- Do not invent facts.
- Keep the answer consolidated and concise.

Question: ${question}

Sources:
${sources || "(no sources retrieved)"}`;
}

export async function generateAnswer(
  question: string,
  pages: RetrievedPage[],
): Promise<GeneratedAnswer> {
  const config = resolveGeminiConfigFromEnv();
  const { client, model } = createGeminiClient(config);

  const response = await client.models.generateContent({
    model,
    contents: buildPrompt(question, pages),
    config: {
      responseMimeType: "application/json",
    },
  });

  const text = response.text?.trim();
  if (!text) {
    return {
      answer: "I could not generate an answer from the available sources.",
      citedPageIds: [],
    };
  }

  try {
    const parsed = JSON.parse(text) as GeneratedAnswer;
    return {
      answer: parsed.answer ?? "I could not generate an answer from the available sources.",
      citedPageIds: Array.isArray(parsed.citedPageIds)
        ? parsed.citedPageIds.map((id) => Number(id)).filter((id) => Number.isFinite(id))
        : [],
    };
  } catch {
    return {
      answer: text,
      citedPageIds: [],
    };
  }
}

export function buildSnippet(content: string, maxLength = 220): string {
  const normalized = content.replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, maxLength - 1)}…`;
}
