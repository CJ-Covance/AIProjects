using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Jira
{
    public interface IJiraClient
    {
        Task<JiraConnectionTestResult> TestConnectionAsync(CancellationToken cancellationToken = default(CancellationToken));

        Task<JiraSearchResult> SearchIssuesAsync(
            string jql,
            int startAt,
            int maxResults,
            CancellationToken cancellationToken = default(CancellationToken));

        Task<IList<JiraIssue>> SearchAllIssuesAsync(
            string jql,
            int pageSize,
            CancellationToken cancellationToken = default(CancellationToken));

        Task<JiraIssue> GetIssueAsync(string issueKey, CancellationToken cancellationToken = default(CancellationToken));

        Task<JiraProject> GetProjectAsync(string projectKey, CancellationToken cancellationToken = default(CancellationToken));
    }
}
