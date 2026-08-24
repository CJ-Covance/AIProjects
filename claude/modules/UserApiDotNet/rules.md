# UserApiDotNet — Rules

1. Preserve Core → Infrastructure → Web layering.
2. PII encryption stays in Infrastructure security helpers (AES).
3. No secrets in source; use config.
4. Do not mix with Atlas Python/TS stacks.
