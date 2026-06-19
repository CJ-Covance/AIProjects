"use client";

import type { Citation } from "@/lib/types";

interface CitationPanelProps {
  citations: Citation[];
  activeIndex: number | null;
  onSelect: (index: number | null) => void;
}

export default function CitationPanel({
  citations,
  activeIndex,
  onSelect,
}: CitationPanelProps) {
  if (citations.length === 0) return null;

  return (
    <div className="atlas-card animate-fade-in p-5">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Source Documents
      </h3>
      <div className="space-y-3">
        {citations.map((citation) => (
          <div
            key={citation.index}
            id={`citation-${citation.index}`}
            className={`rounded-lg border p-4 transition-colors ${
              activeIndex === citation.index
                ? "border-atlas-teal bg-atlas-teal/5"
                : "border-slate-200 hover:border-slate-300"
            }`}
            onClick={() =>
              onSelect(activeIndex === citation.index ? null : citation.index)
            }
          >
            <div className="mb-1 flex items-start gap-2">
              <span className="citation-marker">{citation.index}</span>
              <div className="flex-1">
                <h4 className="font-medium text-atlas-navy">{citation.title}</h4>
                <p className="mt-0.5 text-xs text-slate-500">
                  {citation.source_name} &rsaquo; {citation.domain_name} &rsaquo;{" "}
                  {citation.project_name}
                </p>
              </div>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">
              &ldquo;{citation.snippet}&rdquo;
            </p>
            <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
              <span>
                Updated {new Date(citation.updated_at).toLocaleDateString()}
              </span>
              {citation.url && (
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-atlas-blue hover:underline"
                  onClick={(e) => e.stopPropagation()}
                >
                  Open original &rarr;
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
