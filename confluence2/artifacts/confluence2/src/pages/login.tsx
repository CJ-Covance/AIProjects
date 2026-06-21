export function LoginPage() {
  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 520, margin: "80px auto" }}>
        <h1>Confluence2.0</h1>
        <p className="muted">
          Sign in to add knowledge pages and ask one natural-language question across your
          organization&apos;s content.
        </p>
        <a className="button" href="/api/login">
          Continue with Replit Auth
        </a>
        <p className="muted" style={{ marginTop: 16, fontSize: 14 }}>
          Local development uses a dev auth bypass when Replit integration vars are not set.
        </p>
      </div>
    </div>
  );
}
