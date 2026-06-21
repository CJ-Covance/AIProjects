const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export type User = {
  id: string;
  email?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  profileImageUrl?: string | null;
};

export type Page = {
  id: number;
  title: string;
  content: string;
  domain: string;
  project: string;
  sourceType: string;
  createdAt: string;
  updatedAt: string;
};

export type Citation = {
  pageId: number;
  title: string;
  domain: string;
  project: string;
  snippet: string;
};

export type AskResponse = {
  question: string;
  answer: string;
  citations: Citation[];
  sourcesConsidered: number;
};

export const api = {
  getCurrentUser: () => request<{ user: User | null }>("/api/auth/user"),
  listPages: (params?: { domain?: string; project?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.domain) query.set("domain", params.domain);
    if (params?.project) query.set("project", params.project);
    if (params?.search) query.set("search", params.search);
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request<Page[]>(`/api/pages${suffix}`);
  },
  getPage: (id: number) => request<Page>(`/api/pages/${id}`),
  createPage: (input: { title: string; content: string; domain: string; project: string }) =>
    request<Page>("/api/pages", { method: "POST", body: JSON.stringify(input) }),
  deletePage: (id: number) => request<void>(`/api/pages/${id}`, { method: "DELETE" }),
  getKnowledgeStats: () =>
    request<{
      totalPages: number;
      totalQuestions: number;
      topDomains: Array<{ domain: string; count: number }>;
    }>("/api/knowledge-stats"),
  getWorkspaces: () =>
    request<Array<{ domain: string; project: string; pageCount: number }>>("/api/workspaces"),
  ask: (input: { question: string; domain?: string; project?: string }) =>
    request<AskResponse>("/api/ask", { method: "POST", body: JSON.stringify(input) }),
  getAskHistory: (limit = 20) => request<Array<{
    id: number;
    question: string;
    answer: string;
    citationCount: number;
    createdAt: string;
  }>>(`/api/ask/history?limit=${limit}`),
};
