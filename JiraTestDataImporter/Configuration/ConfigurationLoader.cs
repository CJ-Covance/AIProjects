using System;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace JiraTestDataImporter.Configuration
{
    public static class ConfigurationLoader
    {
        private const string DefaultConfigFileName = "appsettings.json";

        public static AppSettings Load(string configPath = null)
        {
            var path = ResolveConfigPath(configPath);
            if (!File.Exists(path))
            {
                throw new FileNotFoundException(
                    $"Configuration file not found: {path}. Copy appsettings.example.json to appsettings.json and configure it.");
            }

            var json = File.ReadAllText(path);
            var settings = JsonConvert.DeserializeObject<AppSettings>(json);
            if (settings == null)
            {
                throw new InvalidOperationException("Configuration file could not be parsed.");
            }

            ApplyEnvironmentOverrides(settings);
            Validate(settings);
            return settings;
        }

        public static string ResolveConfigPath(string configPath)
        {
            if (!string.IsNullOrWhiteSpace(configPath))
            {
                return Path.GetFullPath(configPath);
            }

            var baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
            return Path.Combine(baseDirectory, DefaultConfigFileName);
        }

        private static void ApplyEnvironmentOverrides(AppSettings settings)
        {
            settings.Jira.BaseUrl = GetEnvironmentOverride("JIRA_BASE_URL", settings.Jira.BaseUrl);
            settings.Jira.ProjectKey = GetEnvironmentOverride("JIRA_PROJECT_KEY", settings.Jira.ProjectKey);
            settings.Jira.User = GetEnvironmentOverride("JIRA_USER", settings.Jira.User);
            settings.Jira.ApiToken = GetEnvironmentOverride("JIRA_API_TOKEN", settings.Jira.ApiToken);
            settings.Jira.ApiVersion = GetEnvironmentOverride("JIRA_API_VERSION", settings.Jira.ApiVersion);
            settings.Jira.Jql = GetEnvironmentOverride("JIRA_JQL", settings.Jira.Jql);

            var pageSize = Environment.GetEnvironmentVariable("JIRA_PAGE_SIZE");
            if (!string.IsNullOrWhiteSpace(pageSize) && int.TryParse(pageSize, out var parsedPageSize))
            {
                settings.Jira.PageSize = parsedPageSize;
            }

            var timeoutSeconds = Environment.GetEnvironmentVariable("JIRA_TIMEOUT_SECONDS");
            if (!string.IsNullOrWhiteSpace(timeoutSeconds) && int.TryParse(timeoutSeconds, out var parsedTimeout))
            {
                settings.Jira.TimeoutSeconds = parsedTimeout;
            }

            settings.Database.ConnectionString = GetEnvironmentOverride(
                "DATABASE_CONNECTION_STRING",
                settings.Database.ConnectionString);

            settings.Application.LogLevel = GetEnvironmentOverride("LOG_LEVEL", settings.Application.LogLevel);

            var dryRun = Environment.GetEnvironmentVariable("DRY_RUN");
            if (!string.IsNullOrWhiteSpace(dryRun) && bool.TryParse(dryRun, out var parsedDryRun))
            {
                settings.Application.DryRun = parsedDryRun;
            }

            var testMode = Environment.GetEnvironmentVariable("TEST_MODE");
            if (!string.IsNullOrWhiteSpace(testMode) && bool.TryParse(testMode, out var parsedTestMode))
            {
                settings.Application.TestMode = parsedTestMode;
            }
        }

        private static string GetEnvironmentOverride(string variableName, string currentValue)
        {
            var value = Environment.GetEnvironmentVariable(variableName);
            return string.IsNullOrWhiteSpace(value) ? currentValue : value.Trim();
        }

        private static void Validate(AppSettings settings)
        {
            if (settings.Jira == null)
            {
                throw new InvalidOperationException("Jira configuration section is required.");
            }

            if (string.IsNullOrWhiteSpace(settings.Jira.BaseUrl))
            {
                throw new InvalidOperationException("Jira:BaseUrl is required.");
            }

            if (string.IsNullOrWhiteSpace(settings.Jira.User))
            {
                throw new InvalidOperationException("Jira:User is required.");
            }

            if (string.IsNullOrWhiteSpace(settings.Jira.ApiToken))
            {
                throw new InvalidOperationException(
                    "Jira:ApiToken is required. Set it in appsettings.json or the JIRA_API_TOKEN environment variable.");
            }

            if (string.IsNullOrWhiteSpace(settings.Jira.Jql))
            {
                throw new InvalidOperationException("Jira:Jql is required.");
            }

            if (settings.Jira.PageSize <= 0)
            {
                throw new InvalidOperationException("Jira:PageSize must be greater than zero.");
            }

            if (settings.Jira.TimeoutSeconds <= 0)
            {
                throw new InvalidOperationException("Jira:TimeoutSeconds must be greater than zero.");
            }

            if (!settings.Application.DryRun && string.IsNullOrWhiteSpace(settings.Database.ConnectionString))
            {
                throw new InvalidOperationException(
                    "Database:ConnectionString is required unless Application:DryRun is true.");
            }
        }
    }
}
