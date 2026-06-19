"use client";

import type { HierarchyNode } from "@/lib/types";

interface ScopeFiltersProps {
  hierarchy: HierarchyNode[];
  sourceId: string;
  domainId: string;
  projectId: string;
  onSourceChange: (id: string) => void;
  onDomainChange: (id: string) => void;
  onProjectChange: (id: string) => void;
}

export default function ScopeFilters({
  hierarchy,
  sourceId,
  domainId,
  projectId,
  onSourceChange,
  onDomainChange,
  onProjectChange,
}: ScopeFiltersProps) {
  const selectedSource = hierarchy.find((s) => s.id === sourceId);
  const domains = selectedSource?.children || [];
  const selectedDomain = domains.find((d) => d.id === domainId);
  const projects = selectedDomain?.children || [];

  return (
    <div className="flex flex-wrap items-center gap-3">
      <span className="text-sm text-slate-500">Scope:</span>
      <select
        className="atlas-select"
        value={sourceId}
        onChange={(e) => onSourceChange(e.target.value)}
      >
        <option value="">All sources</option>
        {hierarchy.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name} ({s.page_count} pages)
          </option>
        ))}
      </select>
      {sourceId && (
        <select
          className="atlas-select"
          value={domainId}
          onChange={(e) => onDomainChange(e.target.value)}
        >
          <option value="">All domains</option>
          {domains.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name} ({d.page_count} pages)
            </option>
          ))}
        </select>
      )}
      {domainId && (
        <select
          className="atlas-select"
          value={projectId}
          onChange={(e) => onProjectChange(e.target.value)}
        >
          <option value="">All projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.page_count} pages)
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
