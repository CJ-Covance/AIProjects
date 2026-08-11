namespace ApiTestConsole.Models
{
    /// <summary>
    /// Result of verifying an AWS CLI profile (equivalent to aws sts get-caller-identity).
    /// </summary>
    public sealed class AwsProfileVerifyResult
    {
        public string ProfileName { get; set; }
        public string Account { get; set; }
        public string Arn { get; set; }
        public string UserId { get; set; }
        public string ConfigFolder { get; set; }
        public string ConfigFile { get; set; }
        public string CredentialsFile { get; set; }
    }
}
