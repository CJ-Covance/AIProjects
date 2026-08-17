using System;
using System.Collections.Generic;
using JiraTestDataImporter.Models;
using JiraTestDataImporter.Services;
using NUnit.Framework;

namespace JiraTestDataImporter.Tests
{
    [TestFixture]
    public class JiraIssueMapperTests
    {
        [Test]
        public void ToTestData_MapsCoreFields()
        {
            var issue = new JiraIssue
            {
                Id = "10001",
                Key = "TEST-101",
                Summary = "Login test",
                Description = "Details",
                Status = "To Do",
                Priority = "High",
                Assignee = "Tester",
                Created = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc),
                Updated = new DateTime(2024, 1, 2, 0, 0, 0, DateTimeKind.Utc),
                ProjectKey = "TEST"
            };

            var result = JiraIssueMapper.ToTestData(issue, "TEST");

            Assert.That(result.JiraIssueKey, Is.EqualTo("TEST-101"));
            Assert.That(result.Summary, Is.EqualTo("Login test"));
            Assert.That(result.Status, Is.EqualTo("To Do"));
            Assert.That(result.ProjectKey, Is.EqualTo("TEST"));
        }

        [Test]
        public void Validate_ReturnsErrorsForMissingKey()
        {
            var record = new TestData
            {
                JiraIssueId = "1",
                JiraIssueKey = ""
            };

            var errors = TestDataValidator.Validate(record);
            Assert.That(errors, Does.Contain("JiraIssueKey is required."));
        }
    }
}
