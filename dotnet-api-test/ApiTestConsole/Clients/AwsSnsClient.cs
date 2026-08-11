using System;
using Amazon;
using Amazon.Runtime;
using Amazon.SimpleNotificationService;
using Amazon.SimpleNotificationService.Model;
using ApiTestConsole.Helpers;
using ApiTestConsole.Models;

namespace ApiTestConsole.Clients
{
    /// <summary>
    /// Calls AWS SNS Publish using locally supplied credentials (equivalent to AWS CLI --profile).
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
        /// Publishes a message to an SNS topic using access key / secret key profile setup.
        /// Mirrors: aws sns publish --profile &lt;name&gt; --region &lt;region&gt; --topic-arn &lt;arn&gt; --message &lt;text&gt;
        /// </summary>
        public AwsSnsPublishResult PublishMessage(
            string profileName,
            string accessKey,
            string secretKey,
            string region,
            string topicArn,
            string message)
        {
            // Local variables for profile/credential setup (passed from UI — not hardcoded)
            var localProfileName = (profileName ?? string.Empty).Trim();
            var localAccessKey = (accessKey ?? string.Empty).Trim();
            var localSecretKey = (secretKey ?? string.Empty).Trim();
            var localRegion = (region ?? string.Empty).Trim();
            var localTopicArn = (topicArn ?? string.Empty).Trim();
            var localMessage = message ?? string.Empty;

            _logger.Info(string.Format("Step: SNS publish started. Profile={0}, Region={1}.", localProfileName, localRegion));
            ValidateInputs(localProfileName, localAccessKey, localSecretKey, localRegion, localTopicArn, localMessage);

            _logger.Info(string.Format("Step: Configuring AWS credentials for profile '{0}'.", localProfileName));
            var credentials = new BasicAWSCredentials(localAccessKey, localSecretKey);
            var regionEndpoint = RegionEndpoint.GetBySystemName(localRegion);

            _logger.Info(string.Format("Step: Creating SNS client for region '{0}'.", localRegion));
            using (var snsClient = new AmazonSimpleNotificationServiceClient(credentials, regionEndpoint))
            {
                var request = new PublishRequest
                {
                    TopicArn = localTopicArn,
                    Message = localMessage
                };

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
                    TopicArn = localTopicArn
                };
            }
        }

        private void ValidateInputs(
            string profileName,
            string accessKey,
            string secretKey,
            string region,
            string topicArn,
            string message)
        {
            if (string.IsNullOrWhiteSpace(profileName))
            {
                throw new ArgumentException("Profile name is required.", "profileName");
            }

            if (string.IsNullOrWhiteSpace(accessKey))
            {
                throw new ArgumentException("Access key is required.", "accessKey");
            }

            if (string.IsNullOrWhiteSpace(secretKey))
            {
                throw new ArgumentException("Secret key is required.", "secretKey");
            }

            if (string.IsNullOrWhiteSpace(region))
            {
                throw new ArgumentException("Region is required.", "region");
            }

            if (string.IsNullOrWhiteSpace(topicArn))
            {
                throw new ArgumentException("Topic ARN is required.", "topicArn");
            }

            if (string.IsNullOrWhiteSpace(message))
            {
                throw new ArgumentException("Message is required.", "message");
            }
        }
    }
}
