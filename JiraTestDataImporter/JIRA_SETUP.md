# Jira Setup Checklist

Use this checklist before running `JiraTestDataImporter`.

## Connection Checklist

- [ ] **Jira URL**  
  Example: `https://company.atlassian.net`

- [ ] **Jira account**  
  Example: `developer@company.com`

- [ ] **Jira authentication / API token**  
  Create at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

- [ ] **Jira project key**  
  Example: `TEST`

- [ ] **Jira project permission**  
  Confirm the account can browse the project and view issues

- [ ] **Issue type**  
  Example: `Test`, `Task`, `Bug`, `Story`

- [ ] **JQL**  
  Example: `project = TEST ORDER BY created DESC`

- [ ] **Required fields**  
  Confirm the project exposes the fields you need to import:
  - Issue ID
  - Issue Key
  - Summary
  - Description
  - Status
  - Priority
  - Issue Type
  - Reporter
  - Assignee
  - Created Date
  - Updated Date
  - Labels
  - Components

## Additional Requirements

- [ ] **Network access**  
  The machine running the importer can reach Jira over HTTPS

- [ ] **SQL Server connection string**  
  Example:

  ```text
  Server=localhost;
  Database=JiraTestDb;
  Integrated Security=True;
  TrustServerCertificate=True;
  ```

- [ ] **Database schema created**  
  Run `Database/SqlScripts/CreateJiraTestDataTable.sql`

## Recommended First Run

1. Set `Application:DryRun` to `true`.
2. Set `Application:TestMode` to `true` if you want a preview prompt.
3. Provide Jira credentials through environment variables when possible:

   ```powershell
   $env:JIRA_USER = "developer@company.com"
   $env:JIRA_API_TOKEN = "<API_TOKEN>"
   $env:JIRA_BASE_URL = "https://company.atlassian.net"
   $env:JIRA_JQL = "project = TEST ORDER BY created DESC"
   ```

4. Run the console application and verify the summary output.
5. Set `Application:DryRun` to `false` for the first real database import.

## Minimum Jira Permissions

- Browse projects
- View issues
- Search issues

If the application will later create or update Jira issues, additional write permissions will be required.

## Security Reminders

- Do not commit API tokens to Git.
- Do not paste tokens into logs or screenshots.
- Prefer a dedicated integration account with read-only access for import-only scenarios.
