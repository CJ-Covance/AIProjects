namespace ApiTestConsole.Models
{
    /// <summary>
    /// Response from AWS SNS Publish, equivalent to CLI JSON output.
    /// </summary>
    public sealed class AwsSnsPublishResult
    {
        public string MessageId { get; set; }
        public string SequenceNumber { get; set; }
        public string HttpStatusCode { get; set; }
        public string ProfileName { get; set; }
        public string Region { get; set; }
        public string TopicArn { get; set; }
        public string CredentialSource { get; set; }
        public string ConfigFolder { get; set; }
    }
}
