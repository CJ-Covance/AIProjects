"use client";

import { useCallback, useEffect, useState } from "react";
import AnswerDisplay from "@/components/AnswerDisplay";
import CitationPanel from "@/components/CitationPanel";
import ScopeFilters from "@/components/ScopeFilters";
import { api } from "@/lib/api";
import type { HierarchyNode, SearchResponse } from "@/lib/types";

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [sourceId, setSourceId] = useState("");
  const [domainId, setDomainId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [activeCitation, setActiveCitation] = useState<number | null>(null);
  const [apiReady, setApiReady] = useState<boolean | null>(null);

  useEffect(() => {
    api
      .getHierarchy()
      .then(setHierarchy)
      .catch(() => setHierarchy([]));
    api
      .health()
      .then((h) => setApiReady(h.openai_configured))
      .catch(() => setApiReady(false));
  }, []);

  const handleSearch = useCallback(async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveCitation(null);
    try {
      const response = await api.search(question, {
        source_id: sourceId || undefined,
        domain_id: domainId || undefined,
        project_id: projectId || undefined,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, [question, sourceId, domainId, projectId]);

  const handleCitationClick = (index: number) => {
    setActiveCitation(index);
    const el = document.getElementById(`citation-${index}`);
    el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  const totalPages = hierarchy.reduce((sum, s) => sum + s.page_count, 0);

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-bold text-atlas-navy">
          Ask once. Get one clear answer.
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-slate-600">
          Atlas searches every relevant page across your connected knowledge sources
          and returns a consolidated, cited answer — so you don&apos;t have to read
          documents one by one.
        </p>
        {totalPages > 0 && (
          <p className="mt-2 text-sm text-slate-400">
            {totalPages} pages indexed across {hierarchy.length} source
            {hierarchy.length !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      {apiReady === false && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          OpenAI API key is not configured on the backend. Search will not generate
          AI answers until <code className="rounded bg-amber-100 px-1">OPENAI_API_KEY</code> is
          set in <code className="rounded bg-amber-100 px-1">backend/.env</code>.
        </div>
      )}

      <div className="atlas-card p-6">
        <div className="mb-4">
          <ScopeFilters
            hierarchy={hierarchy}
            sourceId={sourceId}
            domainId={domainId}
            projectId={projectId}
            onSourceChange={(id) => {
              setSourceId(id);
              setDomainId("");
              setProjectId("");
            }}
            onDomainChange={(id) => {
              setDomainId(id);
              setProjectId("");
            }}
            onProjectChange={setProjectId}
          />
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            className="atlas-input flex-1"
            placeholder="What is our data-retention policy for clinical trial documents?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            className="atlas-btn-primary whitespace-nowrap px-8"
            onClick={handleSearch}
            disabled={loading || !question.trim()}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Searching...
              </span>
            ) : (
              "Ask Atlas"
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-8 space-y-6">
          {(result.folder_paths.length > 0 || result.files_synced > 0) && (
            <p className="text-xs text-slate-500">
              Searched {result.files_synced} file(s) from{" "}
              {result.folder_paths.length} folder path
              {result.folder_paths.length !== 1 ? "s" : ""}
              {result.folder_paths[0] ? `: ${result.folder_paths[0]}` : ""}
            </p>
          )}
          <AnswerDisplay
            answer={result.answer}
            citations={result.citations}
            confidence={result.confidence}
            foundRelevant={result.found_relevant}
            onCitationClick={handleCitationClick}
          />
          {result.citations.length > 0 && (
            <CitationPanel
              citations={result.citations}
              activeIndex={activeCitation}
              onSelect={setActiveCitation}
            />
          )}
        </div>
      )}

      {!result && !loading && (
        <div className="mt-12 grid gap-4 sm:grid-cols-2">
          {[
            "What is our data-retention policy for clinical trial documents?",
            "Which projects are compliant with the data retention policy?",
            "What are the GDPR requirements for clinical data processing?",
            "How do I upload documents to the eTMF system?",
          ].map((q) => (
            <button
              key={q}
              className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-600 transition-colors hover:border-atlas-blue hover:bg-atlas-light/50"
              onClick={() => setQuestion(q)}
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
