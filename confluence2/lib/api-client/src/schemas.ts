import { z } from "zod";

export const userSchema = z.object({
  id: z.string(),
  email: z.string().nullable().optional(),
  firstName: z.string().nullable().optional(),
  lastName: z.string().nullable().optional(),
  profileImageUrl: z.string().nullable().optional(),
});

export const pageSchema = z.object({
  id: z.number(),
  title: z.string(),
  content: z.string(),
  domain: z.string(),
  project: z.string(),
  sourceType: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export const createPageSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
  domain: z.string().min(1),
  project: z.string().min(1),
});

export const askRequestSchema = z.object({
  question: z.string().min(1),
  domain: z.string().optional(),
  project: z.string().optional(),
});

export const citationSchema = z.object({
  pageId: z.number(),
  title: z.string(),
  domain: z.string(),
  project: z.string(),
  snippet: z.string(),
});

export const askResponseSchema = z.object({
  question: z.string(),
  answer: z.string(),
  citations: z.array(citationSchema),
  sourcesConsidered: z.number(),
});

export type User = z.infer<typeof userSchema>;
export type Page = z.infer<typeof pageSchema>;
export type CreatePageInput = z.infer<typeof createPageSchema>;
export type AskRequest = z.infer<typeof askRequestSchema>;
export type AskResponse = z.infer<typeof askResponseSchema>;
export type Citation = z.infer<typeof citationSchema>;
