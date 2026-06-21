import { GoogleGenAI } from "@google/genai";

export type GeminiClientConfig = {
  apiKey: string;
  baseUrl?: string;
  model?: string;
};

export function createGeminiClient(config: GeminiClientConfig) {
  const { apiKey, baseUrl, model = "gemini-2.5-flash" } = config;

  const client = new GoogleGenAI({
    apiKey,
    ...(baseUrl ? { httpOptions: { baseUrl } } : {}),
  });

  return {
    model,
    client,
  };
}

export function resolveGeminiConfigFromEnv(): GeminiClientConfig {
  const replitKey = process.env.AI_INTEGRATIONS_GEMINI_API_KEY;
  const replitBaseUrl = process.env.AI_INTEGRATIONS_GEMINI_BASE_URL;

  if (replitKey && replitBaseUrl) {
    return {
      apiKey: replitKey,
      baseUrl: replitBaseUrl,
    };
  }

  const googleKey = process.env.GOOGLE_API_KEY ?? process.env.GEMINI_API_KEY;
  if (googleKey) {
    return { apiKey: googleKey };
  }

  throw new Error(
    "Gemini is not configured. Set Replit AI integration vars or GOOGLE_API_KEY for local dev.",
  );
}
