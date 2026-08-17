using System;
using System.IO;
using JiraTestDataImporter.Configuration;
using NUnit.Framework;

namespace JiraTestDataImporter.Tests
{
    [TestFixture]
    public class ConfigurationTests
    {
        [Test]
        public void Load_ReadsConfiguredJql()
        {
            var configPath = Path.Combine(TestContext.CurrentContext.TestDirectory, "test-appsettings.json");
            File.WriteAllText(configPath, @"{
  ""Jira"": {
    ""BaseUrl"": ""https://example.atlassian.net"",
    ""ProjectKey"": ""TEST"",
    ""User"": ""user@example.com"",
    ""ApiToken"": ""secret-token"",
    ""ApiVersion"": ""3"",
    ""Jql"": ""project = TEST AND issuetype = Bug"",
    ""PageSize"": 25,
    ""TimeoutSeconds"": 15
  },
  ""Database"": {
    ""ConnectionString"": ""Server=.;Database=JiraTestDb;Integrated Security=True;""
  },
  ""Application"": {
    ""LogLevel"": ""Information"",
    ""EnableDebugLogging"": false,
    ""BatchSize"": 50,
    ""DryRun"": false,
    ""TestMode"": false
  }
}");

            var settings = ConfigurationLoader.Load(configPath);
            Assert.That(settings.Jira.Jql, Is.EqualTo("project = TEST AND issuetype = Bug"));
            Assert.That(settings.Jira.PageSize, Is.EqualTo(25));
        }

        [Test]
        public void Load_RequiresApiToken()
        {
            var configPath = Path.Combine(TestContext.CurrentContext.TestDirectory, "missing-token.json");
            File.WriteAllText(configPath, @"{
  ""Jira"": {
    ""BaseUrl"": ""https://example.atlassian.net"",
    ""User"": ""user@example.com"",
    ""ApiToken"": """",
    ""Jql"": ""project = TEST""
  },
  ""Application"": { ""DryRun"": true }
}");

            var ex = Assert.Throws<InvalidOperationException>(() => ConfigurationLoader.Load(configPath));
            Assert.That(ex.Message, Does.Contain("ApiToken"));
        }
    }
}
