using System;
using System.IO;
using UserApi.Core.Contracts;

namespace UserApi.Infrastructure.Logging
{
    /// <summary>
    /// Lightweight file-based logger for step-by-step flow monitoring.
    /// </summary>
    public sealed class FileLoggerService : ILoggerService
    {
        private readonly string _componentName;
        private readonly object _syncRoot = new object();
        private readonly string _logDirectory;

        public FileLoggerService(string componentName)
        {
            _componentName = string.IsNullOrWhiteSpace(componentName) ? "Application" : componentName;
            _logDirectory = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Logs");
            Directory.CreateDirectory(_logDirectory);
        }

        public void Info(string message)
        {
            Write("INFO", message);
        }

        public void Warn(string message)
        {
            Write("WARN", message);
        }

        public void Error(string message, Exception exception = null)
        {
            var details = exception == null ? message : message + " | " + exception;
            Write("ERROR", details);
        }

        public void Debug(string message)
        {
            Write("DEBUG", message);
        }

        private void Write(string level, string message)
        {
            var line = string.Format(
                "{0:yyyy-MM-dd HH:mm:ss.fff} [{1}] [{2}] {3}",
                DateTime.UtcNow,
                level,
                _componentName,
                message);

            lock (_syncRoot)
            {
                var filePath = Path.Combine(_logDirectory, "application-" + DateTime.UtcNow.ToString("yyyyMMdd") + ".log");
                File.AppendAllText(filePath, line + Environment.NewLine);
            }
        }
    }
}
