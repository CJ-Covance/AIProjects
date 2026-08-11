# .NET Framework 4.8 — User API + API Test Console

Enterprise-grade sample solution demonstrating **layered architecture**, **SOLID/OOP principles**, **AES encryption**, **configuration management**, **Unity DI**, step-by-step **logging**, and an **AWS API test console** with property/value UI.

## Folder Structure

```
dotnet-api-test/
├── ApiTestSolution.sln
├── UserApi.Core/                 # Contracts, domain models, DTOs (abstraction layer)
│   ├── Contracts/
│   ├── DTOs/
│   └── Models/
├── UserApi.Infrastructure/       # Base classes, repositories, services, security
│   ├── Base/                     # BaseRepository, BaseService (inheritance)
│   ├── Helpers/                  # ConfigHelper, ValidationHelper
│   ├── Logging/                  # FileLoggerService
│   ├── Repositories/
│   ├── Security/                 # AesEncryptionService
│   └── Services/                 # UserService, AwsApiService
├── UserApi.Web/                  # ASP.NET Web API 2 (.NET Framework 4.8)
│   ├── App_Start/                # Unity + Web API config
│   ├── Controllers/              # UsersController, AwsController
│   └── Filters/                  # GlobalExceptionFilter
└── ApiTestConsole/               # WinForms test client (User API + AWS IMP tab)
    ├── Clients/
    ├── Helpers/
    └── Models/
```

## Prerequisites

- Windows with **Visual Studio 2019/2022**
- **.NET Framework 4.8 Developer Pack**
- IIS Express (included with Visual Studio)

## Setup

1. Open `ApiTestSolution.sln` in Visual Studio.
2. Restore NuGet packages (Solution → Restore NuGet Packages).
3. Set **multiple startup projects**:
   - `UserApi.Web`
   - `ApiTestConsole`
4. Update configuration keys in:
   - `UserApi.Web/Web.config`
   - `ApiTestConsole/App.config`

### Required Configuration

```xml
<appSettings>
  <add key="EncryptionKey" value="your-long-random-secret" />
  <add key="UserApiBaseUrl" value="http://localhost:44301/api" />
  <add key="AwsApiBaseUrl" value="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod" />
  <add key="AwsApiKey" value="your-api-gateway-key" />
  <add key="AwsRegion" value="us-east-1" />
</appSettings>
```

> **Security:** Never commit real secrets. Use Web.config transforms, environment variables, or Azure Key Vault in production.

## User API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/users` | Create user (email/phone encrypted at rest) |
| GET | `/api/users/{id}` | Fetch user (sensitive fields decrypted in DTO) |
| GET | `/api/users` | List all users |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |
| GET | `/api/aws?path={resource}` | Proxy AWS API; returns flattened property map |

## API Test Console (IMP Notes)

The **AWS API (IMP)** tab:

1. Reads `AwsApiBaseUrl`, `AwsApiKey`, and `AwsRegion` from `App.config`.
2. Calls the configured AWS API Gateway endpoint.
3. Flattens the JSON response into **Property / Value** rows in a grid.
4. Logs every step in the bottom **Step Logger** panel.

The **User API** tab exercises CRUD against the local Web API and displays results in a **PropertyGrid**.

## AWS SNS Publish tab

New **AWS SNS Publish** tab mirrors the CLI command:

```bash
aws sns publish --profile labcorp-connector --region us-east-1 \
  --topic-arn arn:aws:sns:us-east-1:763216446258:labcorpembark-receiving-topic-dev \
  --message "preflig"
```

**UI fields (local variables for profile setup):**

| Field | Purpose |
|-------|---------|
| Profile Name | Logical profile label (e.g. `labcorp-connector`) |
| Access Key | AWS access key ID for credential setup |
| Secret Key | AWS secret access key (masked in UI) |
| Region | e.g. `us-east-1` |
| Topic ARN | SNS topic ARN |
| Message | Message body to publish |

On success, **MessageId** and related properties appear in the Property/Value grid (same as CLI JSON output).

Defaults are loaded from `ApiTestConsole/App.config` (`AwsSnsProfileName`, `AwsSnsRegion`, etc.). Enter **Access Key** and **Secret Key** in the UI — do not commit real credentials.

**NuGet packages required:** `AWSSDK.Core`, `AWSSDK.SimpleNotificationService` (restore packages before build).

### SNS troubleshooting (`HttpErrorResponseException`)

If CLI works (`aws sns publish --profile labcorp-connector ...`) but the app fails:

1. **Leave Access Key and Secret Key empty** — the app will load profile `labcorp-connector` from `%USERPROFILE%\.aws\credentials` (same as CLI).
2. **Temporary credentials** — if you paste keys manually, also paste **Session Token** (required for STS/SSO/temporary keys).
3. **Check the error dialog** — it now shows `ErrorCode`, `HTTP Status`, and `RequestId` from AWS.
4. **Region must match topic ARN** — topic is in `us-east-1`, so Region must be `us-east-1`.
5. **IAM** — profile must have `sns:Publish` on `arn:aws:sns:us-east-1:763216446258:labcorpembark-receiving-topic-dev`.

| AWS ErrorCode | Typical cause |
|---------------|---------------|
| `AccessDenied` / `NotAuthorized` | Missing `sns:Publish` permission |
| `InvalidClientTokenId` | Wrong access key |
| `SignatureDoesNotMatch` | Wrong secret key |
| `ExpiredToken` | Session token expired — refresh creds or use CLI profile file |
| `OptInRequired` | SNS not enabled for account/region |

## OOP Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **Encapsulation** | Private backing fields on `User`; sensitive data stored encrypted; services hide persistence details |
| **Inheritance** | `UserRepository : BaseRepository`, `UserService : BaseService`, `AwsApiService : BaseService` |
| **Abstraction** | `IUserService`, `IUserRepository`, `IEncryptionService`, `IAwsApiService` interfaces |
| **Polymorphism** | Unity resolves interface implementations; `MapToDto` virtual override hook in `UserService` |

## Logging

- **Server:** `Logs/application-YYYYMMDD.log` under the Web API / Infrastructure output directory
- **Console UI:** Real-time step logger in `ApiTestConsole`

## Build Notes

This solution targets **.NET Framework 4.8 only** (not .NET Core/.NET 5+). Build and run on Windows with Visual Studio.

## Troubleshooting: `UserApi.Web` fails to load

If Visual Studio shows:

> The imported project `Microsoft.WebApplication.targets` was not found

**Cause:** `UserApi.Web` is an **IIS-hosted ASP.NET Web API** project. That targets file ships with the Visual Studio **ASP.NET and web development** workload.

**Fix (pick one):**

1. **Install the workload (recommended for full Web API hosting):**
   - Visual Studio Installer → Modify → check **ASP.NET and web development** → Install
   - Reopen the solution

2. **Work with the console app only:**
   - In Solution Explorer, right-click **ApiTestConsole** → **Set as Startup Project**
   - The console calls AWS directly via `AwsApiClient` (IMP tab) and can call a separately hosted User API
   - `UserApi.Web` can remain unloaded if you do not need the local REST server

**Where is the console code?** It is in the **`ApiTestConsole`** project (`MainForm.cs`, `Program.cs`), not in `UserApi.Web`.
