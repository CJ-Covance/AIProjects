import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export function AddKnowledgePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [domain, setDomain] = useState("");
  const [project, setProject] = useState("");

  const createMutation = useMutation({
    mutationFn: api.createPage,
    onSuccess: async (page) => {
      await queryClient.invalidateQueries({ queryKey: ["pages"] });
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      await queryClient.invalidateQueries({ queryKey: ["knowledge-stats"] });
      navigate(`/pages/${page.id}`);
    },
  });

  return (
    <section className="card stack">
      <h1>Add knowledge</h1>
      <p className="muted">Create a manual knowledge page tagged by domain and project.</p>
      <div className="field">
        <label htmlFor="title">Title</label>
        <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="field">
          <label htmlFor="domain">Domain</label>
          <input id="domain" value={domain} onChange={(e) => setDomain(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="project">Project</label>
          <input id="project" value={project} onChange={(e) => setProject(e.target.value)} />
        </div>
      </div>
      <div className="field">
        <label htmlFor="content">Content</label>
        <textarea
          id="content"
          rows={12}
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      </div>
      <button
        className="button"
        disabled={
          !title.trim() ||
          !content.trim() ||
          !domain.trim() ||
          !project.trim() ||
          createMutation.isPending
        }
        onClick={() =>
          createMutation.mutate({
            title: title.trim(),
            content: content.trim(),
            domain: domain.trim(),
            project: project.trim(),
          })
        }
      >
        {createMutation.isPending ? "Saving…" : "Save page"}
      </button>
      {createMutation.error && (
        <p style={{ color: "#d64545" }}>
          {createMutation.error instanceof Error
            ? createMutation.error.message
            : "Failed to save page"}
        </p>
      )}
    </section>
  );
}
