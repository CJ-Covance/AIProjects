# JiraTestDataImporter — Known risks

- Targets .NET Framework 4.8 / Windows — not runnable in the Linux Atlas cloud image without mono/wine (typically reviewed on Windows).
- Live Jira/SQL credentials required for integration runs.
- Schema drift if SQL scripts and repository ADO.NET diverge.
