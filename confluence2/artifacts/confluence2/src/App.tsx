import { useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { AddKnowledgePage } from "./pages/add-knowledge";
import { AskPage } from "./pages/ask";
import { KnowledgeBrowsePage } from "./pages/knowledge-browse";
import { KnowledgeDetailPage } from "./pages/knowledge-detail";
import { LoginPage } from "./pages/login";
import { api } from "./lib/api";

function LoginRoute() {
  const { data, isLoading } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: api.getCurrentUser,
  });

  if (isLoading) {
    return <div className="container">Loading…</div>;
  }

  if (data?.user) {
    return <Navigate to="/" replace />;
  }

  return <LoginPage />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route element={<AppShell />}>
        <Route index element={<AskPage />} />
        <Route path="browse" element={<KnowledgeBrowsePage />} />
        <Route path="add" element={<AddKnowledgePage />} />
        <Route path="pages/:id" element={<KnowledgeDetailPage />} />
      </Route>
    </Routes>
  );
}
