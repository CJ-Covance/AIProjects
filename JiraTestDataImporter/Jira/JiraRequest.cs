using System;
using System.Collections.Generic;

namespace JiraTestDataImporter.Jira
{
    public sealed class JiraRequest
    {
        public JiraRequest(string jql, int startAt, int maxResults, IList<string> fields)
        {
            Jql = jql ?? throw new ArgumentNullException(nameof(jql));
            StartAt = startAt;
            MaxResults = maxResults;
            Fields = fields ?? throw new ArgumentNullException(nameof(fields));
        }

        public string Jql { get; }

        public int StartAt { get; }

        public int MaxResults { get; }

        public IList<string> Fields { get; }
    }
}
