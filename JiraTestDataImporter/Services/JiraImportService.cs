using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Database;
using JiraTestDataImporter.Jira;
using JiraTestDataImporter.Logging;
using JiraTestDataImporter.Models;

namespace JiraTestDataImporter.Services
{
    public sealed class ImportSummary
    {
        public string ProjectKey { get; set; }

        public string Jql { get; set; }

        public int RecordsRead { get; set; }

        public int RecordsAdded { get; set; }

        public int RecordsUpdated { get; set; }

        public int RecordsFailed { get; set; }

        public bool DryRun { get; set; }

        public bool IsSuccessful => RecordsFailed == 0;

        public IList<string> Errors { get; set; } = new List<string>();
    }

    public interface IJiraImportService
    {
        Task<ImportSummary> ImportAsync(CancellationToken cancellationToken = default(CancellationToken));
    }

    public sealed class JiraImportService : IJiraImportService
    {
        private readonly AppSettings _settings;
        private readonly IJiraClient _jiraClient;
        private readonly IDatabaseRepository _databaseRepository;
        private readonly IAppLogger _logger;

        public JiraImportService(
            AppSettings settings,
            IJiraClient jiraClient,
            IDatabaseRepository databaseRepository,
            IAppLogger logger)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
            _jiraClient = jiraClient ?? throw new ArgumentNullException(nameof(jiraClient));
            _databaseRepository = databaseRepository ?? throw new ArgumentNullException(nameof(databaseRepository));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<ImportSummary> ImportAsync(CancellationToken cancellationToken = default(CancellationToken))
        {
            var summary = new ImportSummary
            {
                ProjectKey = _settings.Jira.ProjectKey,
                Jql = _settings.Jira.Jql,
                DryRun = _settings.Application.DryRun
            };

            var startedAt = DateTime.UtcNow;
            _logger.Log(LogLevel.Information, "Starting Jira import process.");

            var connectionResult = await _jiraClient.TestConnectionAsync(cancellationToken).ConfigureAwait(false);
            if (!connectionResult.IsSuccessful)
            {
                summary.Errors.Add(connectionResult.Message);
                summary.RecordsFailed++;
                return summary;
            }

            _logger.Log(LogLevel.Information, connectionResult.Message);

            if (_settings.Application.TestMode)
            {
                var shouldContinue = await RunTestModePromptAsync(cancellationToken).ConfigureAwait(false);
                if (!shouldContinue)
                {
                    _logger.Log(LogLevel.Information, "Import cancelled by user.");
                    return summary;
                }
            }

            IList<JiraIssue> issues;
            try
            {
                issues = await _jiraClient.SearchAllIssuesAsync(
                        _settings.Jira.Jql,
                        _settings.Jira.PageSize,
                        cancellationToken)
                    .ConfigureAwait(false);
            }
            catch (JiraApiException ex)
            {
                summary.Errors.Add(ex.Message);
                summary.RecordsFailed++;
                _logger.Log(LogLevel.Error, ex.Message, ex);
                return summary;
            }

            summary.RecordsRead = issues.Count;

            var validRecords = new List<TestData>();
            foreach (var issue in issues)
            {
                var mapped = JiraIssueMapper.ToTestData(issue, _settings.Jira.ProjectKey);
                var validationErrors = TestDataValidator.Validate(mapped);
                if (validationErrors.Any())
                {
                    summary.RecordsFailed++;
                    var message = $"{issue.Key}: {string.Join(" ", validationErrors)}";
                    summary.Errors.Add(message);
                    _logger.Log(LogLevel.Warning, message);
                    continue;
                }

                validRecords.Add(mapped);
            }

            if (!_settings.Application.DryRun)
            {
                try
                {
                    var dbConnected = await _databaseRepository.TestConnectionAsync(cancellationToken).ConfigureAwait(false);
                    if (!dbConnected)
                    {
                        summary.Errors.Add("Unable to connect to SQL Server.");
                        summary.RecordsFailed += validRecords.Count;
                        return summary;
                    }
                }
                catch (Exception ex)
                {
                    summary.Errors.Add($"SQL connection failure: {ex.Message}");
                    summary.RecordsFailed += validRecords.Count;
                    _logger.Log(LogLevel.Error, summary.Errors.Last(), ex);
                    return summary;
                }
            }

            var upsertResult = await _databaseRepository.UpsertBatchAsync(
                    validRecords,
                    _settings.Application.DryRun,
                    cancellationToken)
                .ConfigureAwait(false);

            summary.RecordsAdded = upsertResult.Inserted;
            summary.RecordsUpdated = upsertResult.Updated;
            summary.RecordsFailed += upsertResult.Failed;
            foreach (var error in upsertResult.Errors)
            {
                summary.Errors.Add(error);
            }

            var elapsed = DateTime.UtcNow - startedAt;
            _logger.Log(
                LogLevel.Information,
                $"Import finished in {elapsed.TotalSeconds:0.00} seconds. Added: {summary.RecordsAdded}, Updated: {summary.RecordsUpdated}, Failed: {summary.RecordsFailed}.");

            return summary;
        }

        private async Task<bool> RunTestModePromptAsync(CancellationToken cancellationToken)
        {
            var preview = await _jiraClient.SearchIssuesAsync(
                    _settings.Jira.Jql,
                    0,
                    Math.Min(_settings.Jira.PageSize, 50),
                    cancellationToken)
                .ConfigureAwait(false);

            Console.WriteLine();
            Console.WriteLine($"Issues found: {preview.Total}");
            Console.WriteLine();
            Console.WriteLine("Sample records:");

            foreach (var issue in preview.Issues.Take(5))
            {
                Console.WriteLine($"{issue.Key} - {issue.Summary}");
            }

            Console.WriteLine();
            Console.Write("Do you want to import these records? (Y/N): ");

            var response = Console.ReadLine();
            return string.Equals(response, "Y", StringComparison.OrdinalIgnoreCase);
        }
    }
}
