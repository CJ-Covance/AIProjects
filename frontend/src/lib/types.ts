export interface Source {
  id: string;
  name: string;
  description: string | null;
  folder_path: string | null;
  resolved_folder_path: string | null;
  created_at: string;
  updated_at: string;
  domain_count: number;
  page_count: number;
}

export interface Domain {
  id: string;
  source_id: string;
  name: string;
  description: string | null;
  folder_path: string | null;
  resolved_folder_path: string | null;
  created_at: string;
  updated_at: string;
  project_count: number;
  page_count: number;
}

export interface Project {
  id: string;
  domain_id: string;
  name: string;
  description: string | null;
  folder_path: string | null;
  resolved_folder_path: string | null;
  created_at: string;
  updated_at: string;
  page_count: number;
}

export interface WebPage {
  id: string;
  project_id: string;
  title: string;
  content: string;
  url: string | null;
  source_file_path: string | null;
  created_at: string;
  updated_at: string;
  chunk_count: number;
}

export interface HierarchyNode {
  id: string;
  name: string;
  type: "source" | "domain" | "project";
  description: string | null;
  folder_path: string | null;
  resolved_folder_path: string | null;
  page_count: number;
  children: HierarchyNode[];
}

export interface Citation {
  index: number;
  web_page_id: string;
  title: string;
  url: string | null;
  snippet: string;
  source_name: string;
  domain_name: string;
  project_name: string;
  updated_at: string;
}

export interface SearchResponse {
  answer: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low" | "none";
  found_relevant: boolean;
  folder_paths: string[];
  files_synced: number;
}

export interface SearchFilters {
  source_id?: string;
  domain_id?: string;
  project_id?: string;
}

export interface FolderSyncResponse {
  project_id: string;
  folder_path: string | null;
  files_found: number;
  results: string[];
  message: string;
}
