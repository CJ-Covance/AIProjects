using System.Collections.Generic;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Jira
{
    public sealed class JiraSearchResult
    {
        public int StartAt { get; set; }

        public int MaxResults { get; set; }

        public int Total { get; set; }

        public IList<JiraIssue> Issues { get; set; } = new List<JiraIssue>();

        public bool HasMore => StartAt + Issues.Count < Total;
    }

    public sealed class JiraConnectionTestResult
    {
        public bool IsSuccessful { get; set; }

        public string Message { get; set; }

        public int IssueCount { get; set; }
    }
}
