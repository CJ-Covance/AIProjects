using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Logging;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Database
{
    public sealed class DatabaseRepository : IDatabaseRepository
    {
        private readonly string _connectionString;
        private readonly IAppLogger _logger;
        private readonly int _batchSize;

        public DatabaseRepository(DatabaseSettings databaseSettings, ApplicationSettings applicationSettings, IAppLogger logger)
        {
            if (databaseSettings == null)
            {
                throw new ArgumentNullException(nameof(databaseSettings));
            }

            if (applicationSettings == null)
            {
                throw new ArgumentNullException(nameof(applicationSettings));
            }

            _connectionString = databaseSettings.ConnectionString;
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _batchSize = applicationSettings.BatchSize > 0 ? applicationSettings.BatchSize : 100;
        }

        public async Task<bool> TestConnectionAsync(CancellationToken cancellationToken = default(CancellationToken))
        {
            using (var connection = CreateConnection())
            {
                await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
                return connection.State == ConnectionState.Open;
            }
        }

        public async Task<bool> ExistsByIssueKeyAsync(string jiraIssueKey, CancellationToken cancellationToken = default(CancellationToken))
        {
            const string sql = "SELECT COUNT(1) FROM JiraTestData WHERE JiraIssueKey = @JiraIssueKey";

            using (var connection = CreateConnection())
            using (var command = new SqlCommand(sql, connection))
            {
                command.Parameters.Add("@JiraIssueKey", SqlDbType.VarChar, 100).Value = jiraIssueKey;
                await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
                var count = (int)await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
                return count > 0;
            }
        }

        public async Task<UpsertResult> UpsertBatchAsync(
            IEnumerable<TestData> records,
            bool dryRun,
            CancellationToken cancellationToken = default(CancellationToken))
        {
            var result = new UpsertResult();

            if (records == null)
            {
                return result;
            }

            foreach (var record in records)
            {
                cancellationToken.ThrowIfCancellationRequested();

                try
                {
                    var exists = await ExistsByIssueKeyAsync(record.JiraIssueKey, cancellationToken).ConfigureAwait(false);
                    if (dryRun)
                    {
                        if (exists)
                        {
                            result.Updated++;
                        }
                        else
                        {
                            result.Inserted++;
                        }

                        continue;
                    }

                    if (exists)
                    {
                        await UpdateAsync(record, cancellationToken).ConfigureAwait(false);
                        result.Updated++;
                    }
                    else
                    {
                        await InsertAsync(record, cancellationToken).ConfigureAwait(false);
                        result.Inserted++;
                    }
                }
                catch (Exception ex)
                {
                    result.Failed++;
                    var message = $"Failed to upsert {record.JiraIssueKey}: {ex.Message}";
                    result.Errors.Add(message);
                    _logger.Log(LogLevel.Error, message, ex);
                }
            }

            return result;
        }

        private async Task InsertAsync(TestData record, CancellationToken cancellationToken)
        {
            const string sql = @"
INSERT INTO JiraTestData
(
    JiraIssueId,
    JiraIssueKey,
    ProjectKey,
    Summary,
    Description,
    Status,
    Priority,
    Assignee,
    CreatedDate,
    UpdatedDate,
    ImportedDate
)
VALUES
(
    @JiraIssueId,
    @JiraIssueKey,
    @ProjectKey,
    @Summary,
    @Description,
    @Status,
    @Priority,
    @Assignee,
    @CreatedDate,
    @UpdatedDate,
    @ImportedDate
);";

            using (var connection = CreateConnection())
            using (var command = new SqlCommand(sql, connection))
            {
                AddCommonParameters(command, record);
                await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
                await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
            }
        }

        private async Task UpdateAsync(TestData record, CancellationToken cancellationToken)
        {
            const string sql = @"
UPDATE JiraTestData
SET
    JiraIssueId = @JiraIssueId,
    ProjectKey = @ProjectKey,
    Summary = @Summary,
    Description = @Description,
    Status = @Status,
    Priority = @Priority,
    Assignee = @Assignee,
    CreatedDate = @CreatedDate,
    UpdatedDate = @UpdatedDate,
    ImportedDate = @ImportedDate
WHERE JiraIssueKey = @JiraIssueKey;";

            using (var connection = CreateConnection())
            using (var command = new SqlCommand(sql, connection))
            {
                AddCommonParameters(command, record);
                await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
                await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
            }
        }

        private static void AddCommonParameters(SqlCommand command, TestData record)
        {
            command.Parameters.Add("@JiraIssueId", SqlDbType.VarChar, 100).Value = (object)record.JiraIssueId ?? DBNull.Value;
            command.Parameters.Add("@JiraIssueKey", SqlDbType.VarChar, 100).Value = record.JiraIssueKey;
            command.Parameters.Add("@ProjectKey", SqlDbType.VarChar, 50).Value = (object)record.ProjectKey ?? DBNull.Value;
            command.Parameters.Add("@Summary", SqlDbType.NVarChar, 500).Value = (object)record.Summary ?? DBNull.Value;
            command.Parameters.Add("@Description", SqlDbType.NVarChar, -1).Value = (object)record.Description ?? DBNull.Value;
            command.Parameters.Add("@Status", SqlDbType.VarChar, 100).Value = (object)record.Status ?? DBNull.Value;
            command.Parameters.Add("@Priority", SqlDbType.VarChar, 100).Value = (object)record.Priority ?? DBNull.Value;
            command.Parameters.Add("@Assignee", SqlDbType.VarChar, 255).Value = (object)record.Assignee ?? DBNull.Value;
            command.Parameters.Add("@CreatedDate", SqlDbType.DateTime).Value = (object)record.CreatedDate ?? DBNull.Value;
            command.Parameters.Add("@UpdatedDate", SqlDbType.DateTime).Value = (object)record.UpdatedDate ?? DBNull.Value;
            command.Parameters.Add("@ImportedDate", SqlDbType.DateTime).Value = record.ImportedDate;
        }

        private SqlConnection CreateConnection()
        {
            return new SqlConnection(_connectionString);
        }
    }
}
