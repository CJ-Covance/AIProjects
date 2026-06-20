"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ActivityLog } from "@/lib/types";

const LEVEL_STYLES: Record<string, string> = {
  ERROR: "bg-red-100 text-red-800 border-red-200",
  WARNING: "bg-amber-100 text-amber-800 border-amber-200",
  INFO: "bg-green-100 text-green-800 border-green-200",
};

export default function LogsPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [total, setTotal] = useState(0);
  const [fileTail, setFileTail] = useState("");
  const [levelFilter, setLevelFilter] = useState("");
  const [pageFilter, setPageFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listLogs({
        level: levelFilter || undefined,
        page: pageFilter || undefined,
        limit: 200,
      });
      setLogs(data.logs);
      setTotal(data.total);
      setFileTail(data.file_tail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load logs");
    } finally {
      setLoading(false);
    }
  }, [levelFilter, pageFilter]);

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 10000);
    return () => clearInterval(interval);
  }, [loadLogs]);

  const handleClear = async () => {
    if (!confirm("Clear all activity logs from the database?")) return;
    try {
      await api.clearLogs();
      await loadLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clear logs");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-atlas-navy">Activity &amp; Error Logs</h1>
          <p className="mt-2 text-slate-600">
            Backend activity, API calls, page saves, uploads, and errors. Use this to diagnose
            issues like &ldquo;failed to fetch&rdquo; when saving web pages.
          </p>
          <p className="mt-1 text-xs text-slate-400">
            API base: <code className="rounded bg-slate-100 px-1">{api.baseUrl}</code> — logs refresh
            every 10 seconds
          </p>
        </div>
        <div className="flex gap-2">
          <button type="button" className="atlas-btn-secondary" onClick={loadLogs}>
            Refresh
          </button>
          <button type="button" className="atlas-btn-secondary text-red-600" onClick={handleClear}>
            Clear logs
          </button>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <select
          className="atlas-select"
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
        >
          <option value="">All levels</option>
          <option value="ERROR">Errors only</option>
          <option value="WARNING">Warnings</option>
          <option value="INFO">Info</option>
        </select>
        <select
          className="atlas-select"
          value={pageFilter}
          onChange={(e) => setPageFilter(e.target.value)}
        >
          <option value="">All pages</option>
          <option value="Manage">Manage</option>
          <option value="Ask">Ask</option>
          <option value="Logs">Logs</option>
        </select>
        <span className="self-center text-sm text-slate-500">{total} total entries</span>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
          <p className="mt-2 text-xs">
            If you see &ldquo;Cannot reach the backend&rdquo;, start the server with:{" "}
            <code className="rounded bg-red-100 px-1">
              python -m uvicorn app.main:app --reload --port 8000
            </code>
          </p>
        </div>
      )}

      {loading && logs.length === 0 ? (
        <p className="text-slate-500">Loading logs...</p>
      ) : logs.length === 0 ? (
        <div className="atlas-card p-8 text-center text-slate-500">
          No log entries yet. Interact with Manage or Ask to generate activity.
        </div>
      ) : (
        <div className="space-y-2">
          {logs.map((log) => (
            <div
              key={log.id}
              className={`atlas-card cursor-pointer p-4 transition-colors hover:border-slate-300 ${
                expanded === log.id ? "border-atlas-blue" : ""
              }`}
              onClick={() => setExpanded(expanded === log.id ? null : log.id)}
            >
              <div className="flex flex-wrap items-start gap-3">
                <span
                  className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${
                    LEVEL_STYLES[log.level] || "bg-slate-100 text-slate-600"
                  }`}
                >
                  {log.level}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium text-atlas-navy">{log.activity}</span>
                    {log.page && (
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                        {log.page}
                      </span>
                    )}
                    <span className="text-xs text-slate-400">
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-700">{log.message}</p>
                  {log.endpoint && (
                    <p className="mt-0.5 text-xs text-slate-400">{log.endpoint}</p>
                  )}
                </div>
              </div>
              {expanded === log.id && (
                <div className="mt-3 border-t border-slate-100 pt-3 text-xs">
                  {log.entity_type && (
                    <p className="text-slate-500">
                      Entity: {log.entity_type} {log.entity_id}
                    </p>
                  )}
                  {log.details && (
                    <pre className="mt-2 overflow-x-auto rounded bg-slate-50 p-3 text-slate-700">
                      {tryFormatJson(log.details)}
                    </pre>
                  )}
                  {log.error_trace && (
                    <pre className="mt-2 overflow-x-auto rounded bg-red-50 p-3 text-red-800">
                      {log.error_trace}
                    </pre>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {fileTail && (
        <div className="mt-8">
          <h2 className="mb-2 text-sm font-semibold text-atlas-navy">Log file tail (atlas.log)</h2>
          <pre className="max-h-64 overflow-auto rounded-lg border border-slate-200 bg-slate-900 p-4 text-xs text-green-300">
            {fileTail}
          </pre>
        </div>
      )}
    </div>
  );
}

function tryFormatJson(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw;
  }
}
