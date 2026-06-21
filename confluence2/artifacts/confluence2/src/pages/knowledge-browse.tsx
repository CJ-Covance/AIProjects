import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export function KnowledgeBrowsePage() {
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [project, setProject] = useState("");

  const pagesQuery = useQuery({
    queryKey: ["pages", search, domain, project],
    queryFn: () =>
      api.listPages({
        search: search.trim() || undefined,
        domain: domain.trim() || undefined,
        project: project.trim() || undefined,
      }),
  });

  const workspacesQuery = useQuery({
    queryKey: ["workspaces"],
    queryFn: api.getWorkspaces,
  });

  const domains = useMemo(
    () => Array.from(new Set(workspacesQuery.data?.map((item) => item.domain) ?? [])),
    [workspacesQuery.data],
  );

  const projects = useMemo(() => {
    const rows = workspacesQuery.data ?? [];
    return Array.from(
      new Set(
        rows
          .filter((item) => !domain || item.domain === domain)
          .map((item) => item.project),
      ),
    );
  }, [workspacesQuery.data, domain]);

  return (
    <div className="stack">
      <section className="card stack">
        <h1>Browse knowledge</h1>
        <div className="grid" style={{ gridTemplateColumns: "2fr 1fr 1fr" }}>
          <div className="field">
            <label htmlFor="search">Search</label>
            <input id="search" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="domain">Domain</label>
            <select id="domain" value={domain} onChange={(e) => setDomain(e.target.value)}>
              <option value="">All</option>
              {domains.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="project">Project</label>
            <select id="project" value={project} onChange={(e) => setProject(e.target.value)}>
              <option value="">All</option>
              {projects.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <section className="card stack">
        {pagesQuery.isLoading && <p>Loading pages…</p>}
        {pagesQuery.data?.length ? (
          pagesQuery.data.map((page) => (
            <article key={page.id} className="stack">
              <div>
                <h2>
                  <Link to={`/pages/${page.id}`}>{page.title}</Link>
                </h2>
                <p className="muted">
                  {page.domain} / {page.project} · {page.sourceType}
                </p>
              </div>
              <p>{page.content.slice(0, 220)}{page.content.length > 220 ? "…" : ""}</p>
            </article>
          ))
        ) : (
          !pagesQuery.isLoading && <p className="muted">No pages found. Add knowledge to get started.</p>
        )}
      </section>
    </div>
  );
}
