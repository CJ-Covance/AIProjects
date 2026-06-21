import type {
  Domain,
  FolderSyncResponse,
  HierarchyNode,
  Project,
  SearchFilters,
  SearchResponse,
  Source,
  WebPage,
  ActivityLog,
  LogsResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = RequestInit & { page?: string };

async function request<T>(path: string, options?: RequestOptions): Promise<T> {
  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string> | undefined),
  };
  if (!(options?.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (options?.page) {
    headers["X-Atlas-Page"] = options.page;
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });
  } catch (err) {
    const hint =
      err instanceof TypeError
        ? `Network error reaching ${API_BASE}. The backend may have crashed mid-request. ` +
          `Confirm it is running: python -m uvicorn app.main:app --reload --port 8000. ` +
          `Open http://localhost:3000/logs (not port 8000).`
        : err instanceof Error
          ? err.message
          : "Network error";
    throw new Error(hint);
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = error.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail) || `Request failed: ${res.status}`
    );
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  baseUrl: API_BASE,

  health: () =>
    request<{
      status: string;
      llm_provider: string;
      embedding_provider: string;
      openai_configured: boolean;
      google_configured: boolean;
      ai_configured: boolean;
      log_file?: string;
    }>("/api/health"),

  getHierarchy: () => request<HierarchyNode[]>("/api/hierarchy"),

  search: (question: string, filters?: SearchFilters) =>
    request<SearchResponse>("/api/search", {
      method: "POST",
      body: JSON.stringify({ question, ...filters }),
      page: "Ask",
    }),

  listLogs: (params?: { level?: string; page?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.level) qs.set("level", params.level);
    if (params?.page) qs.set("page", params.page);
    if (params?.limit) qs.set("limit", String(params.limit));
    const q = qs.toString();
    return request<LogsResponse>(`/api/logs${q ? `?${q}` : ""}`, { page: "Logs" });
  },

  clearLogs: () => request<void>("/api/logs", { method: "DELETE", page: "Logs" }),

  listSources: () => request<Source[]>("/api/sources", { page: "Manage" }),
  createSource: (data: { name: string; description?: string; folder_path?: string }) =>
    request<Source>("/api/sources", { method: "POST", body: JSON.stringify(data), page: "Manage" }),
  updateSource: (id: string, data: { name?: string; description?: string; folder_path?: string }) =>
    request<Source>(`/api/sources/${id}`, { method: "PUT", body: JSON.stringify(data), page: "Manage" }),
  deleteSource: (id: string) =>
    request<void>(`/api/sources/${id}`, { method: "DELETE", page: "Manage" }),

  listDomains: (sourceId?: string) =>
    request<Domain[]>(`/api/domains${sourceId ? `?source_id=${sourceId}` : ""}`, { page: "Manage" }),
  createDomain: (data: {
    source_id: string;
    name: string;
    description?: string;
    folder_path?: string;
  }) => request<Domain>("/api/domains", { method: "POST", body: JSON.stringify(data), page: "Manage" }),
  updateDomain: (id: string, data: { name?: string; description?: string; folder_path?: string }) =>
    request<Domain>(`/api/domains/${id}`, { method: "PUT", body: JSON.stringify(data), page: "Manage" }),
  deleteDomain: (id: string) =>
    request<void>(`/api/domains/${id}`, { method: "DELETE", page: "Manage" }),

  listProjects: (domainId?: string) =>
    request<Project[]>(`/api/projects${domainId ? `?domain_id=${domainId}` : ""}`, { page: "Manage" }),
  createProject: (data: {
    domain_id: string;
    name: string;
    description?: string;
    folder_path?: string;
  }) => request<Project>("/api/projects", { method: "POST", body: JSON.stringify(data), page: "Manage" }),
  updateProject: (id: string, data: { name?: string; description?: string; folder_path?: string }) =>
    request<Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(data), page: "Manage" }),
  deleteProject: (id: string) =>
    request<void>(`/api/projects/${id}`, { method: "DELETE", page: "Manage" }),
  syncProjectFolder: (projectId: string) =>
    request<FolderSyncResponse>(`/api/projects/${projectId}/sync-folder`, {
      method: "POST",
      page: "Manage",
    }),
  uploadProjectFile: async (projectId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/api/projects/${projectId}/upload`, {
        method: "POST",
        body: form,
        headers: { "X-Atlas-Page": "Manage" },
      });
    } catch {
      throw new Error(`Cannot reach backend at ${API_BASE}. Is the server running?`);
    }
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Upload failed");
    }
    return res.json();
  },

  listPages: (projectId?: string) =>
    request<WebPage[]>(`/api/pages${projectId ? `?project_id=${projectId}` : ""}`, { page: "Manage" }),
  getPage: (id: string) => request<WebPage>(`/api/pages/${id}`, { page: "Manage" }),
  createPage: (data: {
    project_id: string;
    title: string;
    content: string;
    url?: string;
    save_to_disk?: boolean;
  }) =>
    request<WebPage>("/api/pages", {
      method: "POST",
      body: JSON.stringify({ save_to_disk: true, ...data }),
      page: "Manage",
    }),
  updatePage: (
    id: string,
    data: { title?: string; content?: string; url?: string; save_to_disk?: boolean }
  ) =>
    request<WebPage>(`/api/pages/${id}`, {
      method: "PUT",
      body: JSON.stringify({ save_to_disk: true, ...data }),
      page: "Manage",
    }),
  deletePage: (id: string) =>
    request<void>(`/api/pages/${id}`, { method: "DELETE", page: "Manage" }),
};

export type { ActivityLog, LogsResponse };
