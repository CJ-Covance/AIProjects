using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Database
{
    public sealed class UpsertResult
    {
        public int Inserted { get; set; }

        public int Updated { get; set; }

        public int Failed { get; set; }

        public IList<string> Errors { get; set; } = new List<string>();
    }

    public interface IDatabaseRepository
    {
        Task<bool> TestConnectionAsync(CancellationToken cancellationToken = default(CancellationToken));

        Task<bool> ExistsByIssueKeyAsync(string jiraIssueKey, CancellationToken cancellationToken = default(CancellationToken));

        Task<UpsertResult> UpsertBatchAsync(
            IEnumerable<TestData> records,
            bool dryRun,
            CancellationToken cancellationToken = default(CancellationToken));
    }
}
