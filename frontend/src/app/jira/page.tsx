"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { JiraIssue, JiraIssueType, JiraPriority, JiraProject } from "@/lib/types";

export default function JiraPage() {
  const [status, setStatus] = useState<{ configured: boolean; connected: boolean; error?: string } | null>(
    null
  );
  const [projects, setProjects] = useState<JiraProject[]>([]);
  const [issueTypes, setIssueTypes] = useState<JiraIssueType[]>([]);
  const [priorities, setPriorities] = useState<JiraPriority[]>([]);

  const [projectKey, setProjectKey] = useState("");
  const [issueType, setIssueType] = useState("");
  const [priority, setPriority] = useState("");
  const [summary, setSummary] = useState("");
  const [description, setDescription] = useState("");
  const [labels, setLabels] = useState("");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdIssue, setCreatedIssue] = useState<JiraIssue | null>(null);

  const loadMetadata = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const jiraStatus = await api.jiraStatus();
      setStatus(jiraStatus);

      if (!jiraStatus.configured) {
        setProjects([]);
        return;
      }

      if (!jiraStatus.connected) {
        setError(jiraStatus.error || "Unable to connect to Jira. Check your credentials.");
        return;
      }

      const [projectList, priorityList] = await Promise.all([
        api.listJiraProjects(),
        api.listJiraPriorities(),
      ]);
      setProjects(projectList);
      setPriorities(priorityList);

      if (projectList.length > 0) {
        setProjectKey((prev) => prev || projectList[0].key);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load Jira metadata");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMetadata();
  }, [loadMetadata]);

  useEffect(() => {
    if (!projectKey) {
      setIssueTypes([]);
      setIssueType("");
      return;
    }

    api
      .listJiraIssueTypes(projectKey)
      .then((types) => {
        setIssueTypes(types);
        setIssueType(types[0]?.name || "");
      })
      .catch(() => setError("Failed to load issue types for the selected project"));
  }, [projectKey]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setCreatedIssue(null);

    try {
      const labelList = labels
        .split(",")
        .map((l) => l.trim())
        .filter(Boolean);

      const issue = await api.createJiraIssue({
        project_key: projectKey,
        summary,
        description,
        issue_type: issueType,
        priority: priority || undefined,
        labels: labelList.length > 0 ? labelList : undefined,
      });
      setCreatedIssue(issue);
      setSummary("");
      setDescription("");
      setLabels("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create Jira issue");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-atlas-navy">Create Jira Issue</h1>
        <p className="mt-2 text-sm text-slate-600">
          Submit a request and it will be stored directly in your Jira project via the REST API.
        </p>
      </div>

      {loading && (
        <div className="atlas-card p-8 text-center text-sm text-slate-500">Loading Jira connection…</div>
      )}

      {!loading && status && !status.configured && (
        <div className="atlas-card border-amber-200 bg-amber-50 p-6">
          <h2 className="font-medium text-amber-900">Jira not configured</h2>
          <p className="mt-2 text-sm text-amber-800">
            Add the following environment variables to the backend <code className="text-xs">.env</code>{" "}
            file:
          </p>
          <ul className="mt-3 list-inside list-disc space-y-1 text-sm text-amber-800">
            <li>
              <code className="text-xs">JIRA_BASE_URL</code> — e.g. https://your-domain.atlassian.net
            </li>
            <li>
              <code className="text-xs">JIRA_EMAIL</code> — your Atlassian account email
            </li>
            <li>
              <code className="text-xs">JIRA_API_TOKEN</code> — API token from Atlassian account settings
            </li>
            <li>
              <code className="text-xs">JIRA_DEFAULT_PROJECT_KEY</code> — optional default project
            </li>
          </ul>
        </div>
      )}

      {!loading && status?.configured && status.connected && (
        <form onSubmit={handleSubmit} className="atlas-card space-y-5 p-6">
          <div>
            <label htmlFor="project" className="mb-1.5 block text-sm font-medium text-slate-700">
              Project
            </label>
            <select
              id="project"
              className="atlas-select w-full"
              value={projectKey}
              onChange={(e) => setProjectKey(e.target.value)}
              required
            >
              {projects.map((p) => (
                <option key={p.id} value={p.key}>
                  {p.name} ({p.key})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="issueType" className="mb-1.5 block text-sm font-medium text-slate-700">
              Issue type
            </label>
            <select
              id="issueType"
              className="atlas-select w-full"
              value={issueType}
              onChange={(e) => setIssueType(e.target.value)}
              required
            >
              {issueTypes.map((t) => (
                <option key={t.id} value={t.name}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="summary" className="mb-1.5 block text-sm font-medium text-slate-700">
              Summary
            </label>
            <input
              id="summary"
              type="text"
              className="atlas-input"
              placeholder="Brief title for the issue"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              required
              maxLength={255}
            />
          </div>

          <div>
            <label htmlFor="description" className="mb-1.5 block text-sm font-medium text-slate-700">
              Description
            </label>
            <textarea
              id="description"
              className="atlas-input min-h-[140px] resize-y"
              placeholder="Detailed description of the request"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={10000}
            />
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label htmlFor="priority" className="mb-1.5 block text-sm font-medium text-slate-700">
                Priority <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <select
                id="priority"
                className="atlas-select w-full"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="">— None —</option>
                {priorities.map((p) => (
                  <option key={p.id} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="labels" className="mb-1.5 block text-sm font-medium text-slate-700">
                Labels <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <input
                id="labels"
                type="text"
                className="atlas-input"
                placeholder="bug, urgent"
                value={labels}
                onChange={(e) => setLabels(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {createdIssue && (
            <div className="animate-fade-in rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              Issue created:{" "}
              {createdIssue.url ? (
                <a
                  href={createdIssue.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold underline hover:text-emerald-900"
                >
                  {createdIssue.key}
                </a>
              ) : (
                <span className="font-semibold">{createdIssue.key}</span>
              )}
            </div>
          )}

          <div className="flex justify-end pt-2">
            <button type="submit" className="atlas-btn-primary" disabled={submitting}>
              {submitting ? "Creating…" : "Create issue in Jira"}
            </button>
          </div>
        </form>
      )}

      {!loading && status?.configured && !status.connected && error && (
        <div className="atlas-card border-red-200 bg-red-50 p-6">
          <h2 className="font-medium text-red-900">Connection failed</h2>
          <p className="mt-2 text-sm text-red-800">{error}</p>
          <button type="button" onClick={loadMetadata} className="atlas-btn-secondary mt-4">
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
