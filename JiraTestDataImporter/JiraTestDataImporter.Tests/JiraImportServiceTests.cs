using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Database;
using JiraTestDataImporter.Jira;
using JiraTestDataImporter.Logging;
using JiraTestDataImporter.Models;
using JiraTestDataImporter.Services;
using Moq;
using Newtonsoft.Json.Linq;
using NUnit.Framework;

namespace JiraTestDataImporter.Tests
{
    [TestFixture]
    public class JiraImportServiceTests
    {
        [Test]
        public async Task ImportAsync_DryRunReportsInsertAndUpdateCounts()
        {
            var settings = CreateSettings(dryRun: true, testMode: false);
            var jiraClient = new Mock<IJiraClient>();
            var repository = new Mock<IDatabaseRepository>();
            var logger = new ConsoleAppLogger("Information", false);

            jiraClient.Setup(x => x.TestConnectionAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(new JiraConnectionTestResult { IsSuccessful = true, Message = "ok", IssueCount = 2 });

            jiraClient.Setup(x => x.SearchAllIssuesAsync(settings.Jira.Jql, settings.Jira.PageSize, It.IsAny<CancellationToken>()))
                .ReturnsAsync(new List<JiraIssue>
                {
                    new JiraIssue { Id = "1", Key = "TEST-1", Summary = "One", ProjectKey = "TEST" },
                    new JiraIssue { Id = "2", Key = "TEST-2", Summary = "Two", ProjectKey = "TEST" }
                });

            repository.Setup(x => x.ExistsByIssueKeyAsync("TEST-1", It.IsAny<CancellationToken>())).ReturnsAsync(false);
            repository.Setup(x => x.ExistsByIssueKeyAsync("TEST-2", It.IsAny<CancellationToken>())).ReturnsAsync(true);

            repository.Setup(x => x.UpsertBatchAsync(It.IsAny<IEnumerable<TestData>>(), true, It.IsAny<CancellationToken>()))
                .ReturnsAsync(new UpsertResult { Inserted = 1, Updated = 1 });

            var service = new JiraImportService(settings, jiraClient.Object, repository.Object, logger);
            var summary = await service.ImportAsync();

            Assert.That(summary.RecordsRead, Is.EqualTo(2));
            Assert.That(summary.RecordsAdded, Is.EqualTo(1));
            Assert.That(summary.RecordsUpdated, Is.EqualTo(1));
            Assert.That(summary.DryRun, Is.True);
        }

        [Test]
        public async Task ImportAsync_AuthenticationFailureStopsImport()
        {
            var settings = CreateSettings(dryRun: true, testMode: false);
            var jiraClient = new Mock<IJiraClient>();
            var repository = new Mock<IDatabaseRepository>();
            var logger = new ConsoleAppLogger("Information", false);

            jiraClient.Setup(x => x.TestConnectionAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(new JiraConnectionTestResult
                {
                    IsSuccessful = false,
                    Message = "Jira authentication failed. Verify the configured user and API token."
                });

            var service = new JiraImportService(settings, jiraClient.Object, repository.Object, logger);
            var summary = await service.ImportAsync();

            Assert.That(summary.IsSuccessful, Is.False);
            Assert.That(summary.Errors[0], Does.Contain("authentication failed"));
            repository.Verify(x => x.UpsertBatchAsync(It.IsAny<IEnumerable<TestData>>(), It.IsAny<bool>(), It.IsAny<CancellationToken>()), Times.Never);
        }

        [Test]
        public async Task ImportAsync_ContinuesWhenSingleRecordValidationFails()
        {
            var settings = CreateSettings(dryRun: true, testMode: false);
            var jiraClient = new Mock<IJiraClient>();
            var repository = new Mock<IDatabaseRepository>();
            var logger = new ConsoleAppLogger("Information", false);

            jiraClient.Setup(x => x.TestConnectionAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(new JiraConnectionTestResult { IsSuccessful = true, IssueCount = 2 });

            jiraClient.Setup(x => x.SearchAllIssuesAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new List<JiraIssue>
                {
                    new JiraIssue { Id = "1", Key = "TEST-1", Summary = "Valid", ProjectKey = "TEST" },
                    new JiraIssue { Id = "", Key = "", Summary = "Invalid", ProjectKey = "TEST" }
                });

            repository.Setup(x => x.UpsertBatchAsync(It.IsAny<IEnumerable<TestData>>(), true, It.IsAny<CancellationToken>()))
                .ReturnsAsync(new UpsertResult { Inserted = 1 });

            var service = new JiraImportService(settings, jiraClient.Object, repository.Object, logger);
            var summary = await service.ImportAsync();

            Assert.That(summary.RecordsRead, Is.EqualTo(2));
            Assert.That(summary.RecordsFailed, Is.EqualTo(1));
            Assert.That(summary.RecordsAdded, Is.EqualTo(1));
        }

        [Test]
        public async Task ImportAsync_SqlFailureIsReported()
        {
            var settings = CreateSettings(dryRun: false, testMode: false);
            var jiraClient = new Mock<IJiraClient>();
            var repository = new Mock<IDatabaseRepository>();
            var logger = new ConsoleAppLogger("Information", false);

            jiraClient.Setup(x => x.TestConnectionAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(new JiraConnectionTestResult { IsSuccessful = true, IssueCount = 1 });

            jiraClient.Setup(x => x.SearchAllIssuesAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new List<JiraIssue>
                {
                    new JiraIssue { Id = "1", Key = "TEST-1", Summary = "Valid", ProjectKey = "TEST" }
                });

            repository.Setup(x => x.TestConnectionAsync(It.IsAny<CancellationToken>()))
                .ThrowsAsync(new InvalidOperationException("Login failed for user"));

            var service = new JiraImportService(settings, jiraClient.Object, repository.Object, logger);
            var summary = await service.ImportAsync();

            Assert.That(summary.IsSuccessful, Is.False);
            Assert.That(summary.Errors[0], Does.Contain("SQL connection failure"));
        }

        [Test]
        public void JiraClient_AuthenticationFailureDoesNotRetry()
        {
            var handler = new SingleResponseHandler(new HttpResponseMessage(HttpStatusCode.Unauthorized)
            {
                Content = new StringContent("Unauthorized", Encoding.UTF8, "application/json")
            });

            var settings = CreateSettings(dryRun: true, testMode: false).Jira;
            using (var client = new JiraClient(settings, new ConsoleAppLogger("Information", false), handler))
            {
                var ex = Assert.ThrowsAsync<JiraApiException>(() => client.GetProjectAsync("TEST"));
                Assert.That(ex.StatusCode, Is.EqualTo(HttpStatusCode.Unauthorized));
            }

            Assert.That(handler.CallCount, Is.EqualTo(1));
        }

        [Test]
        public void JiraClient_RetriesRateLimitResponses()
        {
            var handler = new QueueHttpMessageHandler(new[]
            {
                new HttpResponseMessage((HttpStatusCode)429)
                {
                    Content = new StringContent("Rate limited", Encoding.UTF8, "application/json")
                },
                new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(new JObject
                    {
                        ["id"] = "1",
                        ["key"] = "TEST",
                        ["name"] = "Test Project"
                    }.ToString(), Encoding.UTF8, "application/json")
                }
            });

            var settings = CreateSettings(dryRun: true, testMode: false).Jira;
            using (var client = new JiraClient(settings, new ConsoleAppLogger("Information", false), handler))
            {
                Assert.DoesNotThrowAsync(async () => await client.GetProjectAsync("TEST"));
            }
        }

        private static AppSettings CreateSettings(bool dryRun, bool testMode)
        {
            return new AppSettings
            {
                Jira = new JiraSettings
                {
                    BaseUrl = "https://example.atlassian.net",
                    ProjectKey = "TEST",
                    User = "user@example.com",
                    ApiToken = "token",
                    ApiVersion = "3",
                    Jql = "project = TEST",
                    PageSize = 50,
                    TimeoutSeconds = 30
                },
                Database = new DatabaseSettings
                {
                    ConnectionString = "Server=.;Database=JiraTestDb;Integrated Security=True;"
                },
                Application = new ApplicationSettings
                {
                    DryRun = dryRun,
                    TestMode = testMode,
                    BatchSize = 100
                }
            };
        }
    }

    internal sealed class SingleResponseHandler : HttpMessageHandler
    {
        private readonly HttpResponseMessage _response;
        public int CallCount { get; private set; }

        public SingleResponseHandler(HttpResponseMessage response)
        {
            _response = response;
        }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            CallCount++;
            return Task.FromResult(_response);
        }
    }
}
