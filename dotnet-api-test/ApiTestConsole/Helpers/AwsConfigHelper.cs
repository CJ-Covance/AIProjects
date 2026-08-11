using System;
using System.IO;
using UserApi.Infrastructure.Helpers;

namespace ApiTestConsole.Helpers
{
    /// <summary>
    /// Resolves standard AWS CLI folder paths (e.g. C:\Users\Jainc1\.aws\config).
    /// </summary>
    public static class AwsConfigHelper
    {
        /// <summary>
        /// Returns the .aws folder. Defaults to %USERPROFILE%\.aws unless overridden in App.config.
        /// </summary>
        public static string GetAwsFolder()
        {
            var configured = ConfigHelper.GetAppSetting("AwsConfigFolder", string.Empty);
            if (!string.IsNullOrWhiteSpace(configured))
            {
                return configured.Trim().TrimEnd('\\', '/');
            }

            var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            return Path.Combine(userProfile, ".aws");
        }

        public static string GetConfigFilePath(string awsFolder)
        {
            return Path.Combine(awsFolder, "config");
        }

        public static string GetCredentialsFilePath(string awsFolder)
        {
            return Path.Combine(awsFolder, "credentials");
        }

        public static bool ConfigFileExists(string awsFolder)
        {
            return File.Exists(GetConfigFilePath(awsFolder));
        }

        public static bool CredentialsFileExists(string awsFolder)
        {
            return File.Exists(GetCredentialsFilePath(awsFolder));
        }
    }
}
