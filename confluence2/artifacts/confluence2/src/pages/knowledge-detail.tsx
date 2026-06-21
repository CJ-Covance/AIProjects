import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api";

export function KnowledgeDetailPage() {
  const { id } = useParams();
  const pageId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const pageQuery = useQuery({
    queryKey: ["page", pageId],
    queryFn: () => api.getPage(pageId),
    enabled: Number.isFinite(pageId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deletePage(pageId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["pages"] });
      navigate("/browse");
    },
  });

  if (!Number.isFinite(pageId)) {
    return <p>Invalid page id.</p>;
  }

  if (pageQuery.isLoading) {
    return <p>Loading page…</p>;
  }

  if (!pageQuery.data) {
    return <p>Page not found.</p>;
  }

  const page = pageQuery.data;

  return (
    <section className="card stack">
      <Link to="/browse">← Back to browse</Link>
      <div>
        <h1>{page.title}</h1>
        <p className="muted">
          {page.domain} / {page.project} · updated {new Date(page.updatedAt).toLocaleString()}
        </p>
      </div>
      <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{page.content}</pre>
      <div>
        <button
          className="button danger"
          disabled={deleteMutation.isPending}
          onClick={() => deleteMutation.mutate()}
        >
          Delete page
        </button>
      </div>
    </section>
  );
}
