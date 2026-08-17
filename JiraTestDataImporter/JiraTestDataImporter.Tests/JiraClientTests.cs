using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Jira;
using JiraTestDataImporter.Logging;
using Newtonsoft.Json.Linq;
using NUnit.Framework;

namespace JiraTestDataImporter.Tests
{
    [TestFixture]
    public class JiraClientParsingTests
    {
        [Test]
        public void ParseIssue_MapsExpectedFields()
        {
            var fixturePath = Path.Combine(TestContext.CurrentContext.TestDirectory, "Fixtures", "search-response.json");
            var json = File.ReadAllText(fixturePath);
            var issue = JiraIssueParser.ParseIssue(JObject.Parse(json)["issues"][0]);

            Assert.That(issue.Key, Is.EqualTo("TEST-101"));
            Assert.That(issue.Summary, Is.EqualTo("Login test"));
            Assert.That(issue.Status, Is.EqualTo("To Do"));
            Assert.That(issue.Priority, Is.EqualTo("High"));
            Assert.That(issue.ProjectKey, Is.EqualTo("TEST"));
            Assert.That(issue.Labels, Does.Contain("automation"));
            Assert.That(issue.Components, Does.Contain("Auth"));
        }

        [Test]
        public void ParseIssue_HandlesAdfDescription()
        {
            var fixturePath = Path.Combine(TestContext.CurrentContext.TestDirectory, "Fixtures", "search-response.json");
            var json = File.ReadAllText(fixturePath);
            var issue = JiraIssueParser.ParseIssue(JObject.Parse(json)["issues"][1]);

            Assert.That(issue.Description, Does.Contain("ADF description"));
        }
    }

    [TestFixture]
    public class JiraPaginationTests
    {
        [Test]
        public async Task SearchAllIssuesAsync_RetrievesAllPages()
        {
            var handler = new QueueHttpMessageHandler(new[]
            {
                CreateSearchResponse(startAt: 0, total: 3, keys: new[] { "TEST-1", "TEST-2" }),
                CreateSearchResponse(startAt: 2, total: 3, keys: new[] { "TEST-3" })
            });

            var settings = CreateSettings();
            using (var client = new JiraClient(settings, new ConsoleAppLogger("Information", false), handler))
            {
                var issues = await client.SearchAllIssuesAsync("project = TEST", 2);
                Assert.That(issues.Count, Is.EqualTo(3));
                Assert.That(issues[2].Key, Is.EqualTo("TEST-3"));
            }
        }

        private static HttpResponseMessage CreateSearchResponse(int startAt, int total, string[] keys)
        {
            var issues = new JArray();
            foreach (var key in keys)
            {
                issues.Add(new JObject
                {
                    ["id"] = key.GetHashCode().ToString(),
                    ["key"] = key,
                    ["fields"] = new JObject
                    {
                        ["summary"] = key,
                        ["project"] = new JObject { ["key"] = "TEST" }
                    }
                });
            }

            var payload = new JObject
            {
                ["startAt"] = startAt,
                ["maxResults"] = keys.Length,
                ["total"] = total,
                ["issues"] = issues
            };

            return new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(payload.ToString(), Encoding.UTF8, "application/json")
            };
        }

        private static JiraSettings CreateSettings()
        {
            return new JiraSettings
            {
                BaseUrl = "https://example.atlassian.net",
                User = "user@example.com",
                ApiToken = "token",
                ApiVersion = "3",
                Jql = "project = TEST",
                PageSize = 2,
                TimeoutSeconds = 30
            };
        }
    }

    internal sealed class QueueHttpMessageHandler : HttpMessageHandler
    {
        private readonly Queue<HttpResponseMessage> _responses;

        public QueueHttpMessageHandler(IEnumerable<HttpResponseMessage> responses)
        {
            _responses = new Queue<HttpResponseMessage>(responses);
        }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            if (_responses.Count == 0)
            {
                throw new InvalidOperationException("No queued HTTP responses remain.");
            }

            return Task.FromResult(_responses.Dequeue());
        }
    }
}
