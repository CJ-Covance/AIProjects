"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { Domain, Project, Source, WebPage } from "@/lib/types";

type EntityType = "source" | "domain" | "project" | "page";

interface FormState {
  type: EntityType;
  mode: "create" | "edit";
  id?: string;
  parentId?: string;
  name: string;
  description: string;
  folder_path: string;
  content: string;
  url: string;
  save_to_disk: boolean;
}

const emptyForm = (type: EntityType, parentId?: string): FormState => ({
  type,
  mode: "create",
  parentId,
  name: "",
  description: "",
  folder_path: "",
  content: "",
  url: "",
  save_to_disk: true,
});

const PARENT_LABELS: Record<EntityType, string> = {
  source: "",
  domain: "Source",
  project: "Domain",
  page: "Project",
};

export default function ManagePage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [pages, setPages] = useState<WebPage[]>([]);
  const [allDomains, setAllDomains] = useState<Domain[]>([]);
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [selectedSource, setSelectedSource] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("");
  const [selectedProject, setSelectedProject] = useState("");
  const [form, setForm] = useState<FormState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadSources = useCallback(async () => {
    setSources(await api.listSources());
  }, []);

  const loadDomains = useCallback(async (sourceId: string) => {
    setDomains(await api.listDomains(sourceId || undefined));
  }, []);

  const loadProjects = useCallback(async (domainId: string) => {
    setProjects(await api.listProjects(domainId || undefined));
  }, []);

  const loadPages = useCallback(async (projectId: string) => {
    setPages(await api.listPages(projectId || undefined));
  }, []);

  useEffect(() => {
    loadSources().catch(() => setError("Failed to load sources"));
    api.listDomains().then(setAllDomains).catch(() => {});
    api.listProjects().then(setAllProjects).catch(() => {});
  }, [loadSources]);

  useEffect(() => {
    if (selectedSource) loadDomains(selectedSource).catch(() => {});
    else setDomains([]);
  }, [selectedSource, loadDomains]);

  useEffect(() => {
    if (selectedDomain) loadProjects(selectedDomain).catch(() => {});
    else setProjects([]);
  }, [selectedDomain, loadProjects]);

  useEffect(() => {
    if (selectedProject) loadPages(selectedProject).catch(() => {});
    else setPages([]);
  }, [selectedProject, loadPages]);

  const refreshAll = async () => {
    await loadSources();
    setAllDomains(await api.listDomains());
    setAllProjects(await api.listProjects());
    if (selectedSource) await loadDomains(selectedSource);
    if (selectedDomain) await loadProjects(selectedDomain);
    if (selectedProject) await loadPages(selectedProject);
  };

  const openAddForm = (type: EntityType) => {
    setError(null);
    setInfo(null);
    const parentMap: Record<EntityType, string> = {
      source: "",
      domain: selectedSource,
      project: selectedDomain,
      page: selectedProject,
    };
    const parentId = parentMap[type];
    if (type !== "source" && !parentId) {
      const hint =
        type === "domain"
          ? "Select a Source in the left column first, or choose a parent below."
          : type === "project"
            ? "Select a Domain in the middle columns first, or choose a parent below."
            : "Select a Project first, or choose a parent below.";
      setInfo(hint);
    }
    setForm(emptyForm(type, parentId || undefined));
  };

  const handleSave = async () => {
    if (!form) return;

    if (form.mode === "create") {
      if (form.type === "domain" && !form.parentId) {
        setError("Please select a Source for this domain.");
        return;
      }
      if (form.type === "project" && !form.parentId) {
        setError("Please select a Domain for this project.");
        return;
      }
      if (form.type === "page" && !form.parentId) {
        setError("Please select a Project for this web page.");
        return;
      }
    }

    setSaving(true);
    setError(null);
    try {
      let pageResult: WebPage | null = null;
      if (form.mode === "create") {
        switch (form.type) {
          case "source":
            await api.createSource({
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "domain":
            await api.createDomain({
              source_id: form.parentId!,
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "project":
            await api.createProject({
              domain_id: form.parentId!,
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "page":
            pageResult = await api.createPage({
              project_id: form.parentId!,
              title: form.name,
              content: form.content,
              url: form.url || undefined,
              save_to_disk: form.save_to_disk,
            });
            break;
        }
      } else {
        switch (form.type) {
          case "source":
            await api.updateSource(form.id!, {
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "domain":
            await api.updateDomain(form.id!, {
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "project":
            await api.updateProject(form.id!, {
              name: form.name,
              description: form.description || undefined,
              folder_path: form.folder_path || undefined,
            });
            break;
          case "page":
            pageResult = await api.updatePage(form.id!, {
              title: form.name,
              content: form.content,
              url: form.url || undefined,
              save_to_disk: form.save_to_disk,
            });
            break;
        }
      }
      setForm(null);
      if (pageResult) {
        if (pageResult.disk_path) {
          setInfo(`Page saved to disk: ${pageResult.disk_path}`);
        } else {
          setInfo("Page saved to database.");
        }
        if (pageResult.index_warning) {
          setError(pageResult.index_warning);
        }
      } else {
        setInfo(null);
      }
      await refreshAll();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Save failed";
      setError(msg);
      setInfo("Check the Logs page for detailed error information.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (type: EntityType, id: string, name: string) => {
    if (!confirm(`Delete "${name}" and all its children?`)) return;
    setError(null);
    try {
      switch (type) {
        case "source":
          await api.deleteSource(id);
          if (selectedSource === id) {
            setSelectedSource("");
            setSelectedDomain("");
            setSelectedProject("");
          }
          break;
        case "domain":
          await api.deleteDomain(id);
          if (selectedDomain === id) {
            setSelectedDomain("");
            setSelectedProject("");
          }
          break;
        case "project":
          await api.deleteProject(id);
          if (selectedProject === id) setSelectedProject("");
          break;
        case "page":
          await api.deletePage(id);
          break;
      }
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const handleSyncFolder = async () => {
    if (!selectedProject) {
      setInfo("Select a project to sync files from its folder on disk.");
      return;
    }
    setSyncing(true);
    setError(null);
    try {
      const result = await api.syncProjectFolder(selectedProject);
      setInfo(`${result.message} — folder: ${result.folder_path || "n/a"}`);
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const handleUpload = async (file: File) => {
    if (!selectedProject) {
      setInfo("Select a project before uploading a file.");
      return;
    }
    setSyncing(true);
    setError(null);
    try {
      const result = await api.uploadProjectFile(selectedProject, file);
      setInfo(`Uploaded ${result.filename} to ${result.folder_path}`);
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSyncing(false);
    }
  };

  const selectedProjectData = projects.find((p) => p.id === selectedProject);

  const EntityList = <T extends { id: string; name: string; resolved_folder_path?: string | null }>({
    title,
    items,
    selected,
    onSelect,
    onAdd,
    onEdit,
    onDelete,
    type,
    countKey,
    addHint,
  }: {
    title: string;
    items: T[];
    selected: string;
    onSelect: (id: string) => void;
    onAdd: () => void;
    onEdit: (item: T) => void;
    onDelete: (type: EntityType, id: string, name: string) => void;
    type: EntityType;
    countKey?: keyof T;
    addHint?: string;
  }) => (
    <div className="atlas-card flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div>
          <h3 className="text-sm font-semibold text-atlas-navy">{title}</h3>
          {addHint && <p className="text-xs text-slate-400">{addHint}</p>}
        </div>
        <button type="button" className="text-xs font-medium text-atlas-blue hover:underline" onClick={onAdd}>
          + Add
        </button>
      </div>
      <div className="max-h-80 flex-1 overflow-y-auto">
        {items.length === 0 ? (
          <p className="px-4 py-6 text-center text-xs text-slate-400">None yet — click + Add</p>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className={`border-b border-slate-100 px-4 py-2.5 text-sm transition-colors ${
                selected === item.id ? "bg-atlas-light" : "hover:bg-slate-50"
              }`}
            >
              <div className="flex items-start gap-2">
                <button type="button" className="flex-1 text-left" onClick={() => onSelect(item.id)}>
                  <span className="font-medium text-slate-800">{item.name}</span>
                  {countKey && typeof item[countKey] === "number" && (
                    <span className="ml-2 text-xs text-slate-400">({item[countKey] as number})</span>
                  )}
                  {item.resolved_folder_path && (
                    <p className="mt-0.5 truncate text-xs text-slate-400" title={item.resolved_folder_path}>
                      📁 {item.resolved_folder_path}
                    </p>
                  )}
                </button>
                <button type="button" className="text-xs text-slate-400 hover:text-atlas-blue" onClick={() => onEdit(item)}>
                  Edit
                </button>
                <button
                  type="button"
                  className="text-xs text-slate-400 hover:text-red-500"
                  onClick={() => onDelete(type, item.id, item.name)}
                >
                  Del
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-atlas-navy">Manage Knowledge Base</h1>
        <p className="mt-2 text-slate-600">
          Organize Sources → Domains → Projects → Web Pages. Set folder paths to map each level
          to disk under <code className="rounded bg-slate-100 px-1">backend/knowledge_base/</code>.
          PDF, HTML, Markdown, and text files are read from project folders during search.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {info && (
        <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          {info}
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <EntityList
          title="Sources"
          items={sources}
          selected={selectedSource}
          onSelect={(id) => {
            setSelectedSource(id);
            setSelectedDomain("");
            setSelectedProject("");
          }}
          onAdd={() => openAddForm("source")}
          onEdit={(item) =>
            setForm({
              type: "source",
              mode: "edit",
              id: item.id,
              name: item.name,
              description: ("description" in item ? String(item.description || "") : ""),
              folder_path: ("folder_path" in item ? String(item.folder_path || "") : ""),
              content: "",
              url: "",
              save_to_disk: true,
            })
          }
          onDelete={handleDelete}
          type="source"
          countKey="page_count"
        />
        <EntityList
          title="Domains"
          items={domains}
          selected={selectedDomain}
          onSelect={(id) => {
            setSelectedDomain(id);
            setSelectedProject("");
          }}
          onAdd={() => openAddForm("domain")}
          onEdit={(item) =>
            setForm({
              type: "domain",
              mode: "edit",
              id: item.id,
              parentId: ("source_id" in item ? String(item.source_id) : undefined),
              name: item.name,
              description: ("description" in item ? String(item.description || "") : ""),
              folder_path: ("folder_path" in item ? String(item.folder_path || "") : ""),
              content: "",
              url: "",
              save_to_disk: true,
            })
          }
          onDelete={handleDelete}
          type="domain"
          countKey="page_count"
          addHint={selectedSource ? undefined : "Select a source first"}
        />
        <EntityList
          title="Projects"
          items={projects}
          selected={selectedProject}
          onSelect={setSelectedProject}
          onAdd={() => openAddForm("project")}
          onEdit={(item) =>
            setForm({
              type: "project",
              mode: "edit",
              id: item.id,
              parentId: ("domain_id" in item ? String(item.domain_id) : undefined),
              name: item.name,
              description: ("description" in item ? String(item.description || "") : ""),
              folder_path: ("folder_path" in item ? String(item.folder_path || "") : ""),
              content: "",
              url: "",
              save_to_disk: true,
            })
          }
          onDelete={handleDelete}
          type="project"
          countKey="page_count"
          addHint={selectedDomain ? undefined : "Select a domain first"}
        />
        <EntityList
          title="Web Pages"
          items={pages.map((p) => ({
            ...p,
            name: p.title,
            resolved_folder_path: p.disk_path || p.source_file_path,
          }))}
          selected=""
          onSelect={() => {}}
          onAdd={() => openAddForm("page")}
          onEdit={(item) =>
            setForm({
              type: "page",
              mode: "edit",
              id: item.id,
              parentId: ("project_id" in item ? String(item.project_id) : undefined),
              name: item.name,
              description: "",
              folder_path: "",
              content: "content" in item ? String(item.content) : "",
              url: "url" in item && item.url ? String(item.url) : "",
              save_to_disk: true,
            })
          }
          onDelete={handleDelete}
          type="page"
          countKey="chunk_count"
          addHint={selectedProject ? undefined : "Select a project first"}
        />
      </div>

      {selectedProjectData && (
        <div className="atlas-card mb-6 p-4">
          <h3 className="text-sm font-semibold text-atlas-navy">Project files on disk</h3>
          <p className="mt-1 text-sm text-slate-600">
            Folder:{" "}
            <code className="rounded bg-slate-100 px-1 text-xs">
              {selectedProjectData.resolved_folder_path || "Not configured"}
            </code>
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Place PDF, HTML, HTM, MD, or TXT files in this folder, then sync or ask a question.
          </p>
          <div className="mt-3 flex flex-wrap gap-3">
            <button
              type="button"
              className="atlas-btn-secondary"
              disabled={syncing}
              onClick={handleSyncFolder}
            >
              {syncing ? "Working..." : "Sync folder from disk"}
            </button>
            <button
              type="button"
              className="atlas-btn-secondary"
              disabled={syncing}
              onClick={() => fileInputRef.current?.click()}
            >
              Upload file
            </button>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.html,.htm,.md,.txt"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleUpload(file);
                e.target.value = "";
              }}
            />
          </div>
        </div>
      )}

      {form && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-semibold text-atlas-navy">
              {form.mode === "create" ? "Add" : "Edit"}{" "}
              {form.type === "page" ? "Web Page" : form.type.charAt(0).toUpperCase() + form.type.slice(1)}
            </h2>
            <div className="space-y-4">
              {form.mode === "create" && form.type === "domain" && (
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Source *</label>
                  <select
                    className="atlas-select w-full"
                    value={form.parentId || ""}
                    onChange={(e) => setForm({ ...form, parentId: e.target.value })}
                  >
                    <option value="">Select source...</option>
                    {sources.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              {form.mode === "create" && form.type === "project" && (
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Domain *</label>
                  <select
                    className="atlas-select w-full"
                    value={form.parentId || ""}
                    onChange={(e) => setForm({ ...form, parentId: e.target.value })}
                  >
                    <option value="">Select domain...</option>
                    {allDomains.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              {form.mode === "create" && form.type === "page" && (
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Project *</label>
                  <select
                    className="atlas-select w-full"
                    value={form.parentId || ""}
                    onChange={(e) => setForm({ ...form, parentId: e.target.value })}
                  >
                    <option value="">Select project...</option>
                    {allProjects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  {form.type === "page" ? "Title" : "Name"} *
                </label>
                <input
                  className="atlas-input"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              {form.type !== "page" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
                    <input
                      className="atlas-input"
                      value={form.description}
                      onChange={(e) => setForm({ ...form, description: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      Folder name (optional)
                    </label>
                    <input
                      className="atlas-input"
                      value={form.folder_path}
                      onChange={(e) => setForm({ ...form, folder_path: e.target.value })}
                      placeholder={`Defaults to name, e.g. ${form.name || "My_Folder"}`}
                    />
                    <p className="mt-1 text-xs text-slate-400">
                      Disk path under knowledge_base/{PARENT_LABELS[form.type] ? "..." : ""}
                      {form.type === "source" && "Source"}
                      {form.type === "domain" && "Source/Domain"}
                      {form.type === "project" && "Source/Domain/Project"}
                    </p>
                  </div>
                </>
              )}
              {form.type === "page" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">URL (optional)</label>
                    <input
                      className="atlas-input"
                      value={form.url}
                      onChange={(e) => setForm({ ...form, url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                  <label className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={form.save_to_disk}
                      onChange={(e) => setForm({ ...form, save_to_disk: e.target.checked })}
                    />
                    Save content as .md file in the project folder on disk
                  </label>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">Content</label>
                    <textarea
                      className="atlas-input min-h-[200px] font-mono text-xs"
                      value={form.content}
                      onChange={(e) => setForm({ ...form, content: e.target.value })}
                      placeholder="Paste page content, or use Upload file / Sync folder instead..."
                    />
                  </div>
                  <p className="text-xs text-slate-400">
                    Errors are recorded on the{" "}
                    <a href="/logs" className="text-atlas-blue hover:underline">
                      Logs
                    </a>{" "}
                    page. Backend must be running at {api.baseUrl}.
                  </p>
                </>
              )}
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button type="button" className="atlas-btn-secondary" onClick={() => setForm(null)}>
                Cancel
              </button>
              <button
                type="button"
                className="atlas-btn-primary"
                onClick={handleSave}
                disabled={saving || !form.name.trim()}
              >
                {saving ? "Saving & indexing..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
