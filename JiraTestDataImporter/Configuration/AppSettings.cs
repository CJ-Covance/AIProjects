namespace JiraTestDataImporter.Configuration
{
    public sealed class AppSettings
    {
        public JiraSettings Jira { get; set; } = new JiraSettings();

        public DatabaseSettings Database { get; set; } = new DatabaseSettings();

        public ApplicationSettings Application { get; set; } = new ApplicationSettings();
    }

    public sealed class JiraSettings
    {
        public string BaseUrl { get; set; } = string.Empty;

        public string ProjectKey { get; set; } = string.Empty;

        public string User { get; set; } = string.Empty;

        public string ApiToken { get; set; } = string.Empty;

        public string ApiVersion { get; set; } = "3";

        public string Jql { get; set; } = string.Empty;

        public int PageSize { get; set; } = 50;

        public int TimeoutSeconds { get; set; } = 30;
    }

    public sealed class DatabaseSettings
    {
        public string ConnectionString { get; set; } = string.Empty;
    }

    public sealed class ApplicationSettings
    {
        public string LogLevel { get; set; } = "Information";

        public bool EnableDebugLogging { get; set; }

        public int BatchSize { get; set; } = 100;

        public bool DryRun { get; set; }

        public bool TestMode { get; set; } = true;
    }
}
