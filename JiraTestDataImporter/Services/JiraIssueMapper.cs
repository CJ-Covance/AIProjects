using System;
using System.Collections.Generic;
using System.Linq;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Services
{
    public static class JiraIssueMapper
    {
        public static TestData ToTestData(JiraIssue issue, string fallbackProjectKey)
        {
            if (issue == null)
            {
                throw new ArgumentNullException(nameof(issue));
            }

            return new TestData
            {
                JiraIssueId = issue.Id,
                JiraIssueKey = issue.Key,
                ProjectKey = string.IsNullOrWhiteSpace(issue.ProjectKey) ? fallbackProjectKey : issue.ProjectKey,
                Summary = issue.Summary,
                Description = issue.Description,
                Status = issue.Status,
                Priority = issue.Priority,
                Assignee = issue.Assignee,
                CreatedDate = issue.Created,
                UpdatedDate = issue.Updated,
                ImportedDate = DateTime.UtcNow
            };
        }

        public static IList<TestData> ToTestDataList(IEnumerable<JiraIssue> issues, string fallbackProjectKey)
        {
            return issues.Select(issue => ToTestData(issue, fallbackProjectKey)).ToList();
        }
    }

    public static class TestDataValidator
    {
        public static IList<string> Validate(TestData record)
        {
            var errors = new List<string>();

            if (record == null)
            {
                errors.Add("Record is null.");
                return errors;
            }

            if (string.IsNullOrWhiteSpace(record.JiraIssueId))
            {
                errors.Add("JiraIssueId is required.");
            }

            if (string.IsNullOrWhiteSpace(record.JiraIssueKey))
            {
                errors.Add("JiraIssueKey is required.");
            }

            if (!string.IsNullOrEmpty(record.Summary) && record.Summary.Length > 500)
            {
                errors.Add("Summary exceeds 500 characters.");
            }

            return errors;
        }
    }
}
