import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export function AskPage() {
  const [question, setQuestion] = useState("");
  const [domain, setDomain] = useState("");
  const [project, setProject] = useState("");

  const statsQuery = useQuery({
    queryKey: ["knowledge-stats"],
    queryFn: api.getKnowledgeStats,
  });

  const historyQuery = useQuery({
    queryKey: ["ask-history"],
    queryFn: () => api.getAskHistory(10),
  });

  const askMutation = useMutation({
    mutationFn: api.ask,
    onSuccess: () => {
      historyQuery.refetch();
      statsQuery.refetch();
    },
  });

  return (
    <div className="grid" style={{ gridTemplateColumns: "2fr 1fr" }}>
      <section className="card stack">
        <h1>Ask once</h1>
        <p className="muted">
          Receive one AI-synthesized answer with citations back to the exact source pages.
        </p>
        <div className="field">
          <label htmlFor="question">Question</label>
          <textarea
            id="question"
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What is our data retention policy for clinical trial documents?"
          />
        </div>
        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
          <div className="field">
            <label htmlFor="domain">Domain (optional)</label>
            <input id="domain" value={domain} onChange={(e) => setDomain(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="project">Project (optional)</label>
            <input id="project" value={project} onChange={(e) => setProject(e.target.value)} />
          </div>
        </div>
        <button
          className="button"
          disabled={!question.trim() || askMutation.isPending}
          onClick={() =>
            askMutation.mutate({
              question: question.trim(),
              domain: domain.trim() || undefined,
              project: project.trim() || undefined,
            })
          }
        >
          {askMutation.isPending ? "Thinking…" : "Ask"}
        </button>

        {askMutation.error && (
          <p style={{ color: "#d64545" }}>
            {askMutation.error instanceof Error ? askMutation.error.message : "Ask failed"}
          </p>
        )}

        {askMutation.data && (
          <div className="stack">
            <div>
              <h2>Answer</h2>
              <p>{askMutation.data.answer}</p>
              <p className="muted">
                Considered {askMutation.data.sourcesConsidered} source
                {askMutation.data.sourcesConsidered === 1 ? "" : "s"}.
              </p>
            </div>
            {askMutation.data.citations.length > 0 && (
              <div className="stack">
                <h3>Citations</h3>
                {askMutation.data.citations.map((citation) => (
                  <div key={citation.pageId} className="citation">
                    <strong>
                      <Link to={`/pages/${citation.pageId}`}>{citation.title}</Link>
                    </strong>
                    <div className="muted">
                      {citation.domain} / {citation.project}
                    </div>
                    <p>{citation.snippet}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      <aside className="stack">
        <section className="card stack">
          <h2>Knowledge stats</h2>
          <p>Pages: {statsQuery.data?.totalPages ?? 0}</p>
          <p>Questions asked: {statsQuery.data?.totalQuestions ?? 0}</p>
          {statsQuery.data?.topDomains?.length ? (
            <div>
              <h3>Top domains</h3>
              <ul>
                {statsQuery.data.topDomains.map((item) => (
                  <li key={item.domain}>
                    {item.domain} ({item.count})
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>

        <section className="card stack">
          <h2>Recent questions</h2>
          {historyQuery.data?.length ? (
            historyQuery.data.map((item) => (
              <div key={item.id}>
                <strong>{item.question}</strong>
                <p className="muted">{item.citationCount} citations</p>
              </div>
            ))
          ) : (
            <p className="muted">No questions yet.</p>
          )}
        </section>
      </aside>
    </div>
  );
}
