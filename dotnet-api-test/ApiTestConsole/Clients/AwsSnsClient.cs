using System;
using Amazon;
using Amazon.Runtime;
using Amazon.Runtime.CredentialManagement;
using Amazon.SimpleNotificationService;
using Amazon.SimpleNotificationService.Model;
using ApiTestConsole.Helpers;
using ApiTestConsole.Models;

namespace ApiTestConsole.Clients
{
    /// <summary>
    /// Calls AWS SNS Publish using profile name and/or explicit credentials (equivalent to AWS CLI --profile).
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
        /// Publishes a message to an SNS topic.
        /// Credentials resolution order:
        /// 1) Access Key + Secret Key (+ optional Session Token) from UI
        /// 2) Named profile from %USERPROFILE%\.aws\credentials / .aws\config (same as AWS CLI)
        /// </summary>
        public AwsSnsPublishResult PublishMessage(
            string profileName,
            string accessKey,
            string secretKey,
            string sessionToken,
            string region,
            string topicArn,
            string message)
        {
            var localProfileName = (profileName ?? string.Empty).Trim();
            var localAccessKey = (accessKey ?? string.Empty).Trim();
            var localSecretKey = (secretKey ?? string.Empty).Trim();
            var localSessionToken = (sessionToken ?? string.Empty).Trim();
            var localRegion = (region ?? string.Empty).Trim();
            var localTopicArn = (topicArn ?? string.Empty).Trim();
            var localMessage = message ?? string.Empty;

            _logger.Info(string.Format(
                "Step: SNS publish started. Profile={0}, Region={1}, Topic={2}.",
                localProfileName,
                localRegion,
                localTopicArn));

            ValidateInputs(localProfileName, localRegion, localTopicArn, localMessage);
            ValidateRegionMatchesTopicArn(localRegion, localTopicArn);

            AWSCredentials credentials = ResolveCredentials(
                localProfileName,
                localAccessKey,
                localSecretKey,
                localSessionToken);

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
                        CredentialSource = DescribeCredentialSource(localAccessKey, localSecretKey)
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

        private AWSCredentials ResolveCredentials(
            string profileName,
            string accessKey,
            string secretKey,
            string sessionToken)
        {
            if (!string.IsNullOrWhiteSpace(accessKey) && !string.IsNullOrWhiteSpace(secretKey))
            {
                _logger.Info("Step: Using Access Key + Secret Key from UI.");
                if (!string.IsNullOrWhiteSpace(sessionToken))
                {
                    _logger.Info("Step: Session Token supplied — using temporary credentials.");
                    return new SessionAWSCredentials(accessKey, secretKey, sessionToken);
                }

                return new BasicAWSCredentials(accessKey, secretKey);
            }

            _logger.Info(string.Format(
                "Step: Access Key not supplied — loading profile '{0}' from AWS credentials file (CLI style).",
                profileName));

            var chain = new CredentialProfileStoreChain();
            AWSCredentials profileCredentials;
            if (chain.TryGetAWSCredentials(profileName, out profileCredentials))
            {
                _logger.Info(string.Format(
                    "Step: Profile '{0}' loaded from %USERPROFILE%\\.aws\\credentials or .aws\\config.",
                    profileName));
                return profileCredentials;
            }

            throw new InvalidOperationException(string.Format(
                "Could not load AWS credentials for profile '{0}'.{1}{1}" +
                "Option A — leave Access Key empty and configure CLI profile:{1}" +
                "  %USERPROFILE%\\.aws\\credentials  (same file used by: aws sns publish --profile {0}){1}{1}" +
                "Option B — enter Access Key + Secret Key in the UI.{1}" +
                "  If your keys are temporary (STS/SSO), also enter Session Token.{1}{1}" +
                "Option C — run: aws configure --profile {0}",
                profileName,
                Environment.NewLine));
        }

        private static string DescribeCredentialSource(string accessKey, string secretKey)
        {
            return !string.IsNullOrWhiteSpace(accessKey) && !string.IsNullOrWhiteSpace(secretKey)
                ? "UI (Access Key)"
                : "AWS credentials file profile";
        }

        private static void ValidateRegionMatchesTopicArn(string region, string topicArn)
        {
            // arn:aws:sns:us-east-1:763216446258:topic-name
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
                "{0}{1}{1}ErrorCode: {2}{1}HTTP Status: {3}{1}Message: {4}{1}RequestId: {5}{1}{1}Common fixes:{1}" +
                "- NotAuthorized / AccessDenied: IAM user/role needs sns:Publish on the topic{1}" +
                "- InvalidClientTokenId / SignatureDoesNotMatch: wrong Access Key, Secret Key, or Session Token{1}" +
                "- ExpiredToken: refresh temporary credentials or leave keys empty to use CLI profile{1}" +
                "- OptInRequired: SNS may not be enabled for the account in this region",
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
