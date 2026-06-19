"use client";

import { useCallback, useEffect, useState } from "react";
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
  content: string;
  url: string;
}

const emptyForm = (type: EntityType, parentId?: string): FormState => ({
  type,
  mode: "create",
  parentId,
  name: "",
  description: "",
  content: "",
  url: "",
});

export default function ManagePage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [pages, setPages] = useState<WebPage[]>([]);
  const [selectedSource, setSelectedSource] = useState<string>("");
  const [selectedDomain, setSelectedDomain] = useState<string>("");
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [form, setForm] = useState<FormState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const loadSources = useCallback(async () => {
    const data = await api.listSources();
    setSources(data);
  }, []);

  const loadDomains = useCallback(async (sourceId: string) => {
    const data = await api.listDomains(sourceId || undefined);
    setDomains(data);
  }, []);

  const loadProjects = useCallback(async (domainId: string) => {
    const data = await api.listProjects(domainId || undefined);
    setProjects(data);
  }, []);

  const loadPages = useCallback(async (projectId: string) => {
    const data = await api.listPages(projectId || undefined);
    setPages(data);
  }, []);

  useEffect(() => {
    loadSources().catch(() => setError("Failed to load sources"));
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
    if (selectedSource) await loadDomains(selectedSource);
    if (selectedDomain) await loadProjects(selectedDomain);
    if (selectedProject) await loadPages(selectedProject);
  };

  const handleSave = async () => {
    if (!form) return;
    setSaving(true);
    setError(null);
    try {
      if (form.mode === "create") {
        switch (form.type) {
          case "source":
            await api.createSource({ name: form.name, description: form.description || undefined });
            break;
          case "domain":
            await api.createDomain({
              source_id: form.parentId!,
              name: form.name,
              description: form.description || undefined,
            });
            break;
          case "project":
            await api.createProject({
              domain_id: form.parentId!,
              name: form.name,
              description: form.description || undefined,
            });
            break;
          case "page":
            await api.createPage({
              project_id: form.parentId!,
              title: form.name,
              content: form.content,
              url: form.url || undefined,
            });
            break;
        }
      } else {
        switch (form.type) {
          case "source":
            await api.updateSource(form.id!, {
              name: form.name,
              description: form.description || undefined,
            });
            break;
          case "domain":
            await api.updateDomain(form.id!, {
              name: form.name,
              description: form.description || undefined,
            });
            break;
          case "project":
            await api.updateProject(form.id!, {
              name: form.name,
              description: form.description || undefined,
            });
            break;
          case "page":
            await api.updatePage(form.id!, {
              title: form.name,
              content: form.content,
              url: form.url || undefined,
            });
            break;
        }
      }
      setForm(null);
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
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

  const EntityList = <T extends { id: string; name: string; description?: string | null }>({
    title,
    items,
    selected,
    onSelect,
    onAdd,
    onEdit,
    onDelete,
    type,
    countKey,
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
  }) => (
    <div className="atlas-card flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h3 className="text-sm font-semibold text-atlas-navy">{title}</h3>
        <button className="text-xs font-medium text-atlas-blue hover:underline" onClick={onAdd}>
          + Add
        </button>
      </div>
      <div className="max-h-80 flex-1 overflow-y-auto">
        {items.length === 0 ? (
          <p className="px-4 py-6 text-center text-xs text-slate-400">None yet</p>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className={`flex items-center gap-2 border-b border-slate-100 px-4 py-2.5 text-sm transition-colors ${
                selected === item.id ? "bg-atlas-light" : "hover:bg-slate-50"
              }`}
            >
              <button className="flex-1 text-left" onClick={() => onSelect(item.id)}>
                <span className="font-medium text-slate-800">{item.name}</span>
                {countKey && typeof item[countKey] === "number" && (
                  <span className="ml-2 text-xs text-slate-400">
                    ({item[countKey] as number})
                  </span>
                )}
              </button>
              <button
                className="text-xs text-slate-400 hover:text-atlas-blue"
                onClick={() => onEdit(item)}
              >
                Edit
              </button>
              <button
                className="text-xs text-slate-400 hover:text-red-500"
                onClick={() => onDelete(type, item.id, item.name)}
              >
                Del
              </button>
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
          Add, edit, and organize sources, domains, projects, and web pages. Content
          is automatically indexed for search when pages are added or modified.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <EntityList
          title="Sources"
          items={sources}
          selected={selectedSource}
          onSelect={setSelectedSource}
          onAdd={() => setForm(emptyForm("source"))}
          onEdit={(item) =>
            setForm({
              type: "source",
              mode: "edit",
              id: item.id,
              name: item.name,
              description: item.description || "",
              content: "",
              url: "",
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
          onSelect={setSelectedDomain}
          onAdd={() => selectedSource && setForm(emptyForm("domain", selectedSource))}
          onEdit={(item) =>
            setForm({
              type: "domain",
              mode: "edit",
              id: item.id,
              name: item.name,
              description: item.description || "",
              content: "",
              url: "",
            })
          }
          onDelete={handleDelete}
          type="domain"
          countKey="page_count"
        />
        <EntityList
          title="Projects"
          items={projects}
          selected={selectedProject}
          onSelect={setSelectedProject}
          onAdd={() => selectedDomain && setForm(emptyForm("project", selectedDomain))}
          onEdit={(item) =>
            setForm({
              type: "project",
              mode: "edit",
              id: item.id,
              name: item.name,
              description: item.description || "",
              content: "",
              url: "",
            })
          }
          onDelete={handleDelete}
          type="project"
          countKey="page_count"
        />
        <EntityList
          title="Web Pages"
          items={pages.map((p) => ({ ...p, name: p.title }))}
          selected=""
          onSelect={() => {}}
          onAdd={() => selectedProject && setForm(emptyForm("page", selectedProject))}
          onEdit={(item) =>
            setForm({
              type: "page",
              mode: "edit",
              id: item.id,
              name: item.name,
              description: "",
              content: "content" in item ? String(item.content) : "",
              url: "url" in item && item.url ? String(item.url) : "",
            })
          }
          onDelete={handleDelete}
          type="page"
          countKey="chunk_count"
        />
      </div>

      {form && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-semibold text-atlas-navy">
              {form.mode === "create" ? "Add" : "Edit"}{" "}
              {form.type === "page" ? "Web Page" : form.type.charAt(0).toUpperCase() + form.type.slice(1)}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  {form.type === "page" ? "Title" : "Name"}
                </label>
                <input
                  className="atlas-input"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              {form.type !== "page" && (
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">
                    Description
                  </label>
                  <input
                    className="atlas-input"
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                  />
                </div>
              )}
              {form.type === "page" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      URL (optional)
                    </label>
                    <input
                      className="atlas-input"
                      value={form.url}
                      onChange={(e) => setForm({ ...form, url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      Content
                    </label>
                    <textarea
                      className="atlas-input min-h-[200px] font-mono text-xs"
                      value={form.content}
                      onChange={(e) => setForm({ ...form, content: e.target.value })}
                      placeholder="Paste or write page content here (Markdown supported)..."
                    />
                  </div>
                </>
              )}
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button className="atlas-btn-secondary" onClick={() => setForm(null)}>
                Cancel
              </button>
              <button
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
