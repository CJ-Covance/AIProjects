using System;
using System.Configuration;
using UserApi.Infrastructure.Logging;

namespace UserApi.Infrastructure.Helpers
{
    /// <summary>
    /// Centralized, secure access to application configuration values.
    /// Avoids scattering ConfigurationManager calls across the codebase.
    /// </summary>
    public static class ConfigHelper
    {
        private static readonly FileLoggerService ConfigLogger = new FileLoggerService("ConfigHelper");

        /// <summary>Retrieves a required appSettings value.</summary>
        public static string GetRequiredAppSetting(string key)
        {
            ConfigLogger.Debug(string.Format("Reading required app setting '{0}'.", key));
            var value = ConfigurationManager.AppSettings[key];
            if (string.IsNullOrWhiteSpace(value))
            {
                ConfigLogger.Error(string.Format("Missing or empty configuration key '{0}'.", key));
                throw new ConfigurationErrorsException(
                    string.Format("Required configuration key '{0}' is missing or empty.", key));
            }

            return value.Trim();
        }

        /// <summary>Retrieves an optional appSettings value with a default fallback.</summary>
        public static string GetAppSetting(string key, string defaultValue)
        {
            ConfigLogger.Debug(string.Format("Reading optional app setting '{0}'.", key));
            var value = ConfigurationManager.AppSettings[key];
            return string.IsNullOrWhiteSpace(value) ? defaultValue : value.Trim();
        }

        /// <summary>Retrieves a required connection string.</summary>
        public static string GetRequiredConnectionString(string name)
        {
            ConfigLogger.Debug(string.Format("Reading connection string '{0}'.", name));
            var connection = ConfigurationManager.ConnectionStrings[name];
            if (connection == null || string.IsNullOrWhiteSpace(connection.ConnectionString))
            {
                ConfigLogger.Error(string.Format("Missing connection string '{0}'.", name));
                throw new ConfigurationErrorsException(
                    string.Format("Required connection string '{0}' is missing or empty.", name));
            }

            return connection.ConnectionString;
        }

        /// <summary>Builds the full AWS API URL from base URL and resource path.</summary>
        public static string BuildAwsApiUrl(string resourcePath)
        {
            var baseUrl = GetRequiredAppSetting("AwsApiBaseUrl").TrimEnd('/');
            var path = string.IsNullOrWhiteSpace(resourcePath) ? string.Empty : resourcePath.TrimStart('/');
            var url = string.IsNullOrEmpty(path) ? baseUrl : baseUrl + "/" + path;
            ConfigLogger.Info(string.Format("Resolved AWS API URL: {0}", url));
            return url;
        }
    }
}
