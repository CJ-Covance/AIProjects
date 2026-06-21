import { useQuery } from "@tanstack/react-query";
import { Link, Navigate, Outlet, useLocation } from "react-router-dom";
import { api } from "../lib/api";

export function AppShell() {
  const location = useLocation();
  const { data, isLoading } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: api.getCurrentUser,
  });

  if (isLoading) {
    return <div className="container">Loading…</div>;
  }

  if (!data?.user) {
    return <Navigate to="/login" replace />;
  }

  const links = [
    { to: "/", label: "Ask" },
    { to: "/browse", label: "Browse" },
    { to: "/add", label: "Add Knowledge" },
  ];

  return (
    <div className="container">
      <header className="nav">
        <strong>Confluence2.0</strong>
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={location.pathname === link.to ? "active" : undefined}
          >
            {link.label}
          </Link>
        ))}
        <span className="muted" style={{ marginLeft: "auto" }}>
          {data.user.firstName ?? data.user.email ?? data.user.id}
        </span>
        <a href="/api/logout">Logout</a>
      </header>
      <Outlet />
    </div>
  );
}
