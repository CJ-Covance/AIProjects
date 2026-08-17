using System;

namespace JiraTestDataImporter.Logging
{
    public enum LogLevel
    {
        Debug,
        Information,
        Warning,
        Error
    }

    public interface IAppLogger
    {
        LogLevel MinimumLevel { get; }

        void Log(LogLevel level, string message, Exception exception = null);
    }

    public sealed class ConsoleAppLogger : IAppLogger
    {
        public ConsoleAppLogger(string configuredLevel, bool enableDebugLogging)
        {
            MinimumLevel = ParseLevel(configuredLevel);
            if (enableDebugLogging && MinimumLevel > LogLevel.Debug)
            {
                MinimumLevel = LogLevel.Debug;
            }
        }

        public LogLevel MinimumLevel { get; }

        public void Log(LogLevel level, string message, Exception exception = null)
        {
            if (level < MinimumLevel)
            {
                return;
            }

            var timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss");
            var line = $"[{timestamp}] [{level}] {Sanitize(message)}";
            Console.WriteLine(line);

            if (exception != null)
            {
                Console.WriteLine($"[{timestamp}] [{level}] {Sanitize(exception.Message)}");
            }
        }

        private static LogLevel ParseLevel(string configuredLevel)
        {
            if (Enum.TryParse(configuredLevel, true, out LogLevel level))
            {
                return level;
            }

            return LogLevel.Information;
        }

        private static string Sanitize(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return value;
            }

            return value
                .Replace("Authorization: Basic", "Authorization: [REDACTED]")
                .Replace("ApiToken", "[REDACTED]");
        }
    }
}
