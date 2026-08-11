using System;
using System.IO;
using Amazon;
using Amazon.Runtime;
using Amazon.Runtime.CredentialManagement;
using Amazon.SecurityToken;
using Amazon.SecurityToken.Model;
using Amazon.SimpleNotificationService;
using Amazon.SimpleNotificationService.Model;
using ApiTestConsole.Helpers;
using ApiTestConsole.Models;

namespace ApiTestConsole.Clients
{
    /// <summary>
    /// Calls AWS SNS Publish using the local .aws\config + .aws\credentials profile (same as AWS CLI).
    /// </summary>
    public sealed class AwsSnsClient
    {
        private readonly UiLogger _logger;

        public AwsSnsClient(UiLogger logger)
        {
            _logger = logger ?? throw new ArgumentNullException("logger");
            _logger.Info("AwsSnsClient initialized.");
        }

        /// <summary>
        /// Verifies profile credentials (aws sts get-caller-identity --profile name).
        /// </summary>
        public AwsProfileVerifyResult VerifyProfile(string profileName, string awsConfigFolder, string region)
        {
            var localProfile = (profileName ?? string.Empty).Trim();
            var localFolder = NormalizeAwsFolder(awsConfigFolder);
            var localRegion = (region ?? string.Empty).Trim();

            if (string.IsNullOrWhiteSpace(localProfile))
            {
                throw new ArgumentException("Profile name is required.", "profileName");
            }

            if (string.IsNullOrWhiteSpace(localRegion))
            {
                throw new ArgumentException("Region is required.", "region");
            }

            LogAwsFilePaths(localFolder);
            AWSCredentials credentials = LoadProfileCredentials(localProfile, localFolder);
            var regionEndpoint = RegionEndpoint.GetBySystemName(localRegion);

            _logger.Info(string.Format("Step: Verifying profile '{0}' via STS GetCallerIdentity.", localProfile));
            using (var stsClient = new AmazonSecurityTokenServiceClient(credentials, regionEndpoint))
            {
                try
                {
                    GetCallerIdentityResponse response = stsClient.GetCallerIdentity(new GetCallerIdentityRequest());
                    _logger.Info(string.Format(
                        "Step: Profile verified. Account={0}, Arn={1}.",
                        response.Account,
                        response.Arn));

                    return new AwsProfileVerifyResult
                    {
                        ProfileName = localProfile,
                        Account = response.Account,
                        Arn = response.Arn,
                        UserId = response.UserId,
                        ConfigFolder = localFolder,
                        ConfigFile = AwsConfigHelper.GetConfigFilePath(localFolder),
                        CredentialsFile = AwsConfigHelper.GetCredentialsFilePath(localFolder)
                    };
                }
                catch (AmazonServiceException ex)
                {
                    throw BuildAwsException("Profile verification rejected by AWS.", ex);
                }
            }
        }

        public AwsSnsPublishResult PublishMessage(
            bool useAwsConfigFile,
            string awsConfigFolder,
            string profileName,
            string accessKey,
            string secretKey,
            string sessionToken,
            string region,
            string topicArn,
            string message)
        {
            var localFolder = NormalizeAwsFolder(awsConfigFolder);
            var localProfileName = (profileName ?? string.Empty).Trim();
            var localAccessKey = (accessKey ?? string.Empty).Trim();
            var localSecretKey = (secretKey ?? string.Empty).Trim();
            var localSessionToken = (sessionToken ?? string.Empty).Trim();
            var localRegion = (region ?? string.Empty).Trim();
            var localTopicArn = (topicArn ?? string.Empty).Trim();
            var localMessage = message ?? string.Empty;

            _logger.Info(string.Format(
                "Step: SNS publish started. UseAwsConfig={0}, Profile={1}, Region={2}.",
                useAwsConfigFile,
                localProfileName,
                localRegion));

            ValidateInputs(localProfileName, localRegion, localTopicArn, localMessage);
            ValidateRegionMatchesTopicArn(localRegion, localTopicArn);

            AWSCredentials credentials = useAwsConfigFile
                ? LoadProfileCredentials(localProfileName, localFolder)
                : LoadManualCredentials(localAccessKey, localSecretKey, localSessionToken);

            var credentialSource = useAwsConfigFile
                ? string.Format("AWS .aws profile ({0})", localProfileName)
                : "Manual Access Key";

            RegionEndpoint regionEndpoint = RegionEndpoint.GetBySystemName(localRegion);

            _logger.Info(string.Format("Step: Creating SNS client for region '{0}'.", localRegion));
            using (var snsClient = new AmazonSimpleNotificationServiceClient(credentials, regionEndpoint))
            {
                var request = new PublishRequest
                {
                    TopicArn = localTopicArn,
                    Message = localMessage
                };

                try
                {
                    _logger.Info(string.Format("Step: Publishing message to topic '{0}'.", localTopicArn));
                    PublishResponse response = snsClient.Publish(request);
                    _logger.Info(string.Format("Step: SNS publish succeeded. MessageId={0}.", response.MessageId));

                    return new AwsSnsPublishResult
                    {
                        MessageId = response.MessageId,
                        SequenceNumber = response.SequenceNumber,
                        HttpStatusCode = response.HttpStatusCode.ToString(),
                        ProfileName = localProfileName,
                        Region = localRegion,
                        TopicArn = localTopicArn,
                        CredentialSource = credentialSource,
                        ConfigFolder = localFolder
                    };
                }
                catch (AmazonServiceException ex)
                {
                    throw BuildAwsException("SNS Publish rejected by AWS.", ex);
                }
                catch (AmazonClientException ex)
                {
                    throw BuildAwsClientException("SNS client error.", ex);
                }
            }
        }

        private AWSCredentials LoadProfileCredentials(string profileName, string awsConfigFolder)
        {
            LogAwsFilePaths(awsConfigFolder);

            var credentialsFile = AwsConfigHelper.GetCredentialsFilePath(awsConfigFolder);
            if (!File.Exists(credentialsFile) && !AwsConfigHelper.ConfigFileExists(awsConfigFolder))
            {
                throw new InvalidOperationException(string.Format(
                    "AWS config folder not found or empty:{0}{0}  Folder: {1}{0}  Expected: {2}{0}  Expected: {3}{0}{0}" +
                    "Create these files (same as AWS CLI) or update the AWS Config Folder path in the UI.",
                    Environment.NewLine,
                    awsConfigFolder,
                    AwsConfigHelper.GetConfigFilePath(awsConfigFolder),
                    credentialsFile));
            }

            _logger.Info(string.Format(
                "Step: Loading profile '{0}' from AWS CLI files (config + credentials).",
                profileName));

            var chain = new CredentialProfileStoreChain(credentialsFile);
            AWSCredentials profileCredentials;
            if (chain.TryGetAWSCredentials(profileName, out profileCredentials))
            {
                _logger.Info(string.Format("Step: Profile '{0}' loaded successfully.", profileName));
                return profileCredentials;
            }

            throw new InvalidOperationException(string.Format(
                "Profile '{0}' was not found in:{1}  {2}{1}  {3}{1}{1}" +
                "Ensure the profile exists (run: aws configure list-profiles) and matches AWS CLI.",
                profileName,
                Environment.NewLine,
                AwsConfigHelper.GetConfigFilePath(awsConfigFolder),
                credentialsFile));
        }

        private AWSCredentials LoadManualCredentials(string accessKey, string secretKey, string sessionToken)
        {
            if (string.IsNullOrWhiteSpace(accessKey) || string.IsNullOrWhiteSpace(secretKey))
            {
                throw new ArgumentException(
                    "Access Key and Secret Key are required when not using the .aws config folder.",
                    "accessKey");
            }

            _logger.Info("Step: Using manual Access Key + Secret Key from UI.");
            if (!string.IsNullOrWhiteSpace(sessionToken))
            {
                _logger.Info("Step: Session Token supplied — using temporary credentials.");
                return new SessionAWSCredentials(accessKey, secretKey, sessionToken);
            }

            return new BasicAWSCredentials(accessKey, secretKey);
        }

        private void LogAwsFilePaths(string awsConfigFolder)
        {
            var configPath = AwsConfigHelper.GetConfigFilePath(awsConfigFolder);
            var credentialsPath = AwsConfigHelper.GetCredentialsFilePath(awsConfigFolder);

            _logger.Info(string.Format("Step: AWS config folder = {0}", awsConfigFolder));
            _logger.Info(string.Format(
                "Step: config file = {0} ({1})",
                configPath,
                File.Exists(configPath) ? "found" : "missing"));
            _logger.Info(string.Format(
                "Step: credentials file = {0} ({1})",
                credentialsPath,
                File.Exists(credentialsPath) ? "found" : "missing"));
        }

        private static string NormalizeAwsFolder(string awsConfigFolder)
        {
            if (!string.IsNullOrWhiteSpace(awsConfigFolder))
            {
                return awsConfigFolder.Trim().TrimEnd('\\', '/');
            }

            return AwsConfigHelper.GetAwsFolder();
        }

        private static void ValidateRegionMatchesTopicArn(string region, string topicArn)
        {
            var parts = topicArn.Split(':');
            if (parts.Length >= 4 && parts[0] == "arn" && parts[2] == "sns")
            {
                var topicRegion = parts[3];
                if (!string.Equals(topicRegion, region, StringComparison.OrdinalIgnoreCase))
                {
                    throw new ArgumentException(string.Format(
                        "Region '{0}' does not match Topic ARN region '{1}'. Use --region {1}.",
                        region,
                        topicRegion),
                        "region");
                }
            }
        }

        private InvalidOperationException BuildAwsException(string prefix, AmazonServiceException ex)
        {
            var details = string.Format(
                "{0}{1}{1}ErrorCode: {2}{1}HTTP Status: {3}{1}Message: {4}{1}RequestId: {5}",
                prefix,
                Environment.NewLine,
                ex.ErrorCode ?? "(none)",
                ex.StatusCode,
                ex.Message,
                ex.RequestId ?? "(none)");

            _logger.Error(details, ex);
            return new InvalidOperationException(details, ex);
        }

        private InvalidOperationException BuildAwsClientException(string prefix, AmazonClientException ex)
        {
            var details = string.Format("{0}{1}{1}Message: {2}", prefix, Environment.NewLine, ex.Message);
            _logger.Error(details, ex);
            return new InvalidOperationException(details, ex);
        }

        private void ValidateInputs(string profileName, string region, string topicArn, string message)
        {
            if (string.IsNullOrWhiteSpace(profileName))
            {
                throw new ArgumentException("Profile name is required.", "profileName");
            }

            if (string.IsNullOrWhiteSpace(region))
            {
                throw new ArgumentException("Region is required.", "region");
            }

            if (string.IsNullOrWhiteSpace(topicArn))
            {
                throw new ArgumentException("Topic ARN is required.", "topicArn");
            }

            if (!topicArn.StartsWith("arn:aws:sns:", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException("Topic ARN must start with arn:aws:sns:", "topicArn");
            }

            if (string.IsNullOrWhiteSpace(message))
            {
                throw new ArgumentException("Message is required.", "message");
            }
        }
    }
}
