"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { APP_NAME } from "@/lib/app";
import type { HierarchyNode } from "@/lib/types";
import Link from "next/link";

function TreeNode({
  node,
  depth = 0,
}: {
  node: HierarchyNode;
  depth?: number;
}) {
  const [expanded, setExpanded] = useState(depth < 2);
  const hasChildren = node.children.length > 0;
  const typeIcons: Record<string, string> = {
    source: "📚",
    domain: "🏢",
    project: "📁",
  };

  return (
    <div className={depth > 0 ? "ml-6 border-l border-slate-200 pl-4" : ""}>
      <div
        className={`flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors ${
          hasChildren ? "cursor-pointer hover:bg-slate-50" : ""
        }`}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren && (
          <span className="text-xs text-slate-400">{expanded ? "▼" : "▶"}</span>
        )}
        <span>{typeIcons[node.type] || "📄"}</span>
        <div className="flex-1">
          <span className="font-medium text-atlas-navy">{node.name}</span>
          {node.description && (
            <p className="text-xs text-slate-500">{node.description}</p>
          )}
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600">
          {node.page_count} page{node.page_count !== 1 ? "s" : ""}
        </span>
        {node.type === "project" && (
          <Link
            href={`/?project=${node.id}`}
            className="text-xs text-atlas-blue hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            Ask about this
          </Link>
        )}
      </div>
      {expanded &&
        node.children.map((child) => (
          <TreeNode key={child.id} node={child} depth={depth + 1} />
        ))}
    </div>
  );
}

export default function BrowsePage() {
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getHierarchy()
      .then(setHierarchy)
      .catch(() => setHierarchy([]))
      .finally(() => setLoading(false));
  }, []);

  const totalPages = hierarchy.reduce((sum, s) => sum + s.page_count, 0);
  const totalDomains = hierarchy.reduce((sum, s) => sum + s.children.length, 0);
  const totalProjects = hierarchy.reduce(
    (sum, s) => sum + s.children.reduce((ds, d) => ds + d.children.length, 0),
    0
  );

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-atlas-navy">Browse Knowledge</h1>
        <p className="mt-2 text-slate-600">
          Explore the domains and projects {APP_NAME} knows about. Select an area to
          focus your next question.
        </p>
      </div>

      <div className="mb-8 grid grid-cols-3 gap-4">
        {[
          { label: "Sources", value: hierarchy.length },
          { label: "Domains", value: totalDomains },
          { label: "Pages indexed", value: totalPages },
        ].map((stat) => (
          <div key={stat.label} className="atlas-card p-4 text-center">
            <div className="text-2xl font-bold text-atlas-navy">{stat.value}</div>
            <div className="text-sm text-slate-500">{stat.label}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-slate-500">Loading hierarchy...</div>
      ) : hierarchy.length === 0 ? (
        <div className="atlas-card p-8 text-center">
          <p className="text-slate-600">No knowledge sources configured yet.</p>
          <Link href="/manage" className="mt-3 inline-block text-atlas-blue hover:underline">
            Add your first source &rarr;
          </Link>
        </div>
      ) : (
        <div className="atlas-card p-4">
          {hierarchy.map((source) => (
            <TreeNode key={source.id} node={source} />
          ))}
        </div>
      )}

      {totalProjects > 0 && (
        <p className="mt-4 text-center text-sm text-slate-400">
          {totalProjects} project{totalProjects !== 1 ? "s" : ""} across{" "}
          {totalDomains} domain{totalDomains !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  );
}
