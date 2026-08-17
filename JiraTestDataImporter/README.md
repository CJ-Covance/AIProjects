# Jira Test Data Importer

A modular .NET Framework 4.8 console application that connects to Jira Cloud through the REST API, executes configurable JQL, and imports issue data into Microsoft SQL Server using an upsert workflow.

The project is intentionally structured so the console host can later be replaced by an ASP.NET Web API without rewriting the Jira or database layers.

## Architecture

```
JiraTestDataImporter
│
├── Models/              Jira and database domain models
├── Jira/                IJiraClient, HTTP integration, pagination, retry
├── Database/            IDatabaseRepository, ADO.NET upsert logic, SQL scripts
├── Services/            Import orchestration and mapping
├── Configuration/       JSON settings and environment overrides
├── Logging/             Basic console logging
└── Program.cs           Startup and summary output only
```

Import flow:

```
Console -> Load Configuration -> Test Jira -> Execute JQL -> Paginate Results
       -> Map to TestData -> Validate -> Upsert SQL Server -> Print Summary
```

## Prerequisites

- Windows build/runtime environment for .NET Framework 4.8, or the .NET SDK with `net48` reference assemblies for cross-platform builds
- Access to Jira Cloud over HTTPS
- A Jira account with API token authentication
- Microsoft SQL Server database
- Jira permissions to browse projects and search/view issues

## Quick Start

1. Clone the repository.
2. Copy `appsettings.example.json` to `appsettings.json`.
3. Configure Jira and SQL Server settings.
4. Run the SQL script in `Database/SqlScripts/CreateJiraTestDataTable.sql`.
5. Build and run the console application.

```powershell
cd JiraTestDataImporter
dotnet build JiraTestDataImporter.sln
dotnet run --project JiraTestDataImporter\JiraTestDataImporter.csproj
```

On first run, keep `Application:DryRun` set to `true` to validate Jira connectivity and record counts without writing to SQL Server.

## Jira Setup

See [JIRA_SETUP.md](./JIRA_SETUP.md) for a beginner-friendly checklist.

### Required Jira Values

| Setting | Description | Example |
|---|---|---|
| `Jira:BaseUrl` | Jira Cloud site URL | `https://your-company.atlassian.net` |
| `Jira:ProjectKey` | Project key | `TEST` |
| `Jira:User` | Jira account email | `developer@company.com` |
| `Jira:ApiToken` | Jira API token | Set via config or `JIRA_API_TOKEN` |
| `Jira:ApiVersion` | REST API version | `3` |
| `Jira:Jql` | Query to execute | `project = TEST ORDER BY created DESC` |
| `Jira:PageSize` | Page size for search | `50` |
| `Jira:TimeoutSeconds` | HTTP timeout | `30` |

### Required Jira Permissions

The integration account should have at least:

- Browse projects
- View issues
- Search issues

Read-only access is sufficient for import-only usage.

### Jira API Authentication

For Jira Cloud:

1. Sign in at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
2. Create an API token.
3. Set `Jira:User` to your Atlassian account email.
4. Set `Jira:ApiToken` in environment variables or local config.

The application uses HTTP Basic authentication with `email:api_token`.

Never commit API tokens to Git.

### Retrieved Jira Fields

The importer requests these Jira fields:

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
- Project Key

## SQL Server Setup

Run:

```sql
-- File: Database/SqlScripts/CreateJiraTestDataTable.sql
```

Example connection string:

```text
Server=localhost;
Database=JiraTestDb;
Integrated Security=True;
TrustServerCertificate=True;
```

The table uses a unique index on `JiraIssueKey` to prevent duplicate records. Existing keys are updated on subsequent runs.

## Configuration

Configuration is loaded from `appsettings.json` in the application output directory. Environment variables override file values.

Supported environment variables:

- `JIRA_BASE_URL`
- `JIRA_PROJECT_KEY`
- `JIRA_USER`
- `JIRA_API_TOKEN`
- `JIRA_API_VERSION`
- `JIRA_JQL`
- `JIRA_PAGE_SIZE`
- `JIRA_TIMEOUT_SECONDS`
- `DATABASE_CONNECTION_STRING`
- `LOG_LEVEL`
- `DRY_RUN`
- `TEST_MODE`

Example configuration:

```json
{
  "Jira": {
    "BaseUrl": "https://your-company.atlassian.net",
    "ProjectKey": "TEST",
    "User": "your-account@company.com",
    "ApiToken": "",
    "ApiVersion": "3",
    "Jql": "project = TEST ORDER BY created DESC",
    "PageSize": 50,
    "TimeoutSeconds": 30
  },
  "Database": {
    "ConnectionString": "Server=localhost;Database=JiraTestDb;Integrated Security=True;TrustServerCertificate=True;"
  },
  "Application": {
    "LogLevel": "Information",
    "EnableDebugLogging": true,
    "BatchSize": 100,
    "DryRun": true,
    "TestMode": false
  }
}
```

### Application Options

- `DryRun`: connect to Jira, validate, and report insert/update counts without modifying SQL Server
- `TestMode`: after a successful Jira connection, show the first five issues and prompt `Y/N` before importing
- `BatchSize`: reserved batch size setting for repository processing

## Example JQL

```jql
project = TEST
project = TEST AND issuetype = Bug
project = TEST AND updated >= -7d
project = TEST AND status = "In Progress" ORDER BY updated DESC
```

## Example Output

```text
=========================================
JIRA TEST DATA IMPORT
=========================================

Jira Project  : TEST
JQL           : project = TEST ORDER BY created DESC
Dry Run       : True
Records Read  : 25
Records Added : 10
Records Updated: 15
Records Failed: 0

Dry run completed successfully.

=========================================
```

## Test Mode Example

```text
Jira connection successful.

Issues found: 25

Sample records:

TEST-101 - Login test
TEST-102 - User registration test
TEST-103 - Password reset test

Do you want to import these records? (Y/N):
```

## Unit Tests

```powershell
dotnet test JiraTestDataImporter\JiraTestDataImporter.sln
```

Tests mock `IJiraClient` and `IDatabaseRepository` so no live Jira or SQL Server instance is required.

Coverage includes:

- Jira JSON parsing
- Configurable JQL loading
- Pagination
- Jira-to-database mapping
- Duplicate detection behavior through dry-run upsert counts
- Authentication and API failure handling
- SQL connection failure handling
- Retry behavior for transient HTTP failures

## Troubleshooting

| Problem | Likely Cause | Action |
|---|---|---|
| Authentication failed | Wrong email or token | Regenerate API token and verify `Jira:User` |
| Invalid JQL | Unsupported JQL syntax | Test the query in Jira Advanced Search |
| Project not found | Wrong project key or missing permission | Verify project key and browse permission |
| HTTP 429 | Rate limiting | Reduce page size or rerun later; retry logic is built in |
| SQL connection failure | Invalid connection string or DB offline | Verify SQL Server availability and credentials |
| No records imported | Dry run enabled | Set `Application:DryRun` to `false` |

## Security Recommendations

- Store API tokens in environment variables or a secret store.
- Do not commit `appsettings.json` with real credentials.
- Use a dedicated Jira integration account with read-only permissions where possible.
- Restrict SQL credentials to the minimum required for insert/update operations.
- Keep HTTPS enabled for all Jira calls.

## Known Limitations

- Jira Cloud REST API v3 is assumed.
- Rich-text Jira descriptions in Atlassian Document Format are stored as JSON text rather than rendered plain text.
- The console host prompts for confirmation only when `TestMode` is enabled.
- Live Jira connectivity was not validated in this environment because no real Jira credentials were available.

## Recommended Next Steps

- Extract the service and repository layers into class libraries for reuse in ASP.NET Web API.
- Add scheduled execution through Windows Task Scheduler or a worker service.
- Expand field mapping for custom Jira fields.
- Add structured logging such as Serilog if centralized logging becomes necessary.
- Add integration tests against a dedicated Jira sandbox and SQL Server test database.
