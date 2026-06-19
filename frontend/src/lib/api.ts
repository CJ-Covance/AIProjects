import type {
  Domain,
  HierarchyNode,
  Project,
  SearchFilters,
  SearchResponse,
  Source,
  WebPage,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  health: () => request<{ status: string; openai_configured: boolean }>("/api/health"),

  getHierarchy: () => request<HierarchyNode[]>("/api/hierarchy"),

  search: (question: string, filters?: SearchFilters) =>
    request<SearchResponse>("/api/search", {
      method: "POST",
      body: JSON.stringify({ question, ...filters }),
    }),

  // Sources
  listSources: () => request<Source[]>("/api/sources"),
  createSource: (data: { name: string; description?: string }) =>
    request<Source>("/api/sources", { method: "POST", body: JSON.stringify(data) }),
  updateSource: (id: string, data: { name?: string; description?: string }) =>
    request<Source>(`/api/sources/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSource: (id: string) => request<void>(`/api/sources/${id}`, { method: "DELETE" }),

  // Domains
  listDomains: (sourceId?: string) =>
    request<Domain[]>(`/api/domains${sourceId ? `?source_id=${sourceId}` : ""}`),
  createDomain: (data: { source_id: string; name: string; description?: string }) =>
    request<Domain>("/api/domains", { method: "POST", body: JSON.stringify(data) }),
  updateDomain: (id: string, data: { name?: string; description?: string }) =>
    request<Domain>(`/api/domains/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteDomain: (id: string) => request<void>(`/api/domains/${id}`, { method: "DELETE" }),

  // Projects
  listProjects: (domainId?: string) =>
    request<Project[]>(`/api/projects${domainId ? `?domain_id=${domainId}` : ""}`),
  createProject: (data: { domain_id: string; name: string; description?: string }) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify(data) }),
  updateProject: (id: string, data: { name?: string; description?: string }) =>
    request<Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<void>(`/api/projects/${id}`, { method: "DELETE" }),

  // Pages
  listPages: (projectId?: string) =>
    request<WebPage[]>(`/api/pages${projectId ? `?project_id=${projectId}` : ""}`),
  getPage: (id: string) => request<WebPage>(`/api/pages/${id}`),
  createPage: (data: { project_id: string; title: string; content: string; url?: string }) =>
    request<WebPage>("/api/pages", { method: "POST", body: JSON.stringify(data) }),
  updatePage: (
    id: string,
    data: { title?: string; content?: string; url?: string }
  ) => request<WebPage>(`/api/pages/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deletePage: (id: string) => request<void>(`/api/pages/${id}`, { method: "DELETE" }),
};
