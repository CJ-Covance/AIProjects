using System;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Database;
using JiraTestDataImporter.Jira;
using JiraTestDataImporter.Logging;
using JiraTestDataImporter.Services;

namespace JiraTestDataImporter
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            IAppLogger logger = null;

            try
            {
                var configPath = args.Length > 0 ? args[0] : null;
                var settings = ConfigurationLoader.Load(configPath);

                logger = new ConsoleAppLogger(
                    settings.Application.LogLevel,
                    settings.Application.EnableDebugLogging);

                logger.Log(LogLevel.Information, "Application startup.");

                using (var jiraClient = new JiraClient(settings.Jira, logger))
                {
                    IDatabaseRepository databaseRepository = new DatabaseRepository(
                        settings.Database,
                        settings.Application,
                        logger);

                    var importService = new JiraImportService(
                        settings,
                        jiraClient,
                        databaseRepository,
                        logger);

                    var summary = importService.ImportAsync(CancellationToken.None).GetAwaiter().GetResult();
                    PrintSummary(summary);

                    return summary.IsSuccessful ? 0 : 1;
                }
            }
            catch (Exception ex)
            {
                if (logger != null)
                {
                    logger.Log(LogLevel.Error, "Application failed.", ex);
                }
                else
                {
                    Console.WriteLine($"Application failed: {ex.Message}");
                }

                return 1;
            }
        }

        private static void PrintSummary(ImportSummary summary)
        {
            Console.WriteLine();
            Console.WriteLine("=========================================");
            Console.WriteLine("JIRA TEST DATA IMPORT");
            Console.WriteLine("=========================================");
            Console.WriteLine();
            Console.WriteLine($"Jira Project  : {summary.ProjectKey}");
            Console.WriteLine($"JQL           : {summary.Jql}");
            Console.WriteLine($"Dry Run       : {summary.DryRun}");
            Console.WriteLine($"Records Read  : {summary.RecordsRead}");
            Console.WriteLine($"Records Added : {summary.RecordsAdded}");
            Console.WriteLine($"Records Updated: {summary.RecordsUpdated}");
            Console.WriteLine($"Records Failed: {summary.RecordsFailed}");
            Console.WriteLine();

            if (summary.Errors.Count > 0)
            {
                Console.WriteLine("Failures:");
                foreach (var error in summary.Errors)
                {
                    Console.WriteLine($"- {error}");
                }

                Console.WriteLine();
            }

            if (summary.IsSuccessful)
            {
                Console.WriteLine(summary.DryRun
                    ? "Dry run completed successfully."
                    : "Import completed successfully.");
            }
            else
            {
                Console.WriteLine("Import completed with failures.");
            }

            Console.WriteLine();
            Console.WriteLine("=========================================");
        }
    }
}
