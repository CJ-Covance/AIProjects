using System;
using System.Collections.Generic;

namespace JiraTestDataImporter.Models
{
    public sealed class JiraIssue
    {
        public string Id { get; set; }

        public string Key { get; set; }

        public string Summary { get; set; }

        public string Description { get; set; }

        public string Status { get; set; }

        public string Priority { get; set; }

        public string IssueType { get; set; }

        public string Reporter { get; set; }

        public string Assignee { get; set; }

        public DateTime? Created { get; set; }

        public DateTime? Updated { get; set; }

        public IList<string> Labels { get; set; } = new List<string>();

        public IList<string> Components { get; set; } = new List<string>();

        public string ProjectKey { get; set; }
    }

    public sealed class JiraProject
    {
        public string Id { get; set; }

        public string Key { get; set; }

        public string Name { get; set; }
    }

    public sealed class JiraStatus
    {
        public string Id { get; set; }

        public string Name { get; set; }
    }

    public sealed class TestData
    {
        public int TestDataId { get; set; }

        public string JiraIssueId { get; set; }

        public string JiraIssueKey { get; set; }

        public string ProjectKey { get; set; }

        public string Summary { get; set; }

        public string Description { get; set; }

        public string Status { get; set; }

        public string Priority { get; set; }

        public string Assignee { get; set; }

        public DateTime? CreatedDate { get; set; }

        public DateTime? UpdatedDate { get; set; }

        public DateTime ImportedDate { get; set; } = DateTime.UtcNow;
    }
}
