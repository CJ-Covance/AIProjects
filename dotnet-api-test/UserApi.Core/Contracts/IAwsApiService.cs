using System.Collections.Generic;

namespace UserApi.Core.Contracts
{
    /// <summary>
    /// Contract for calling external AWS-hosted APIs and returning flat key/value results for UI binding.
    /// </summary>
    public interface IAwsApiService
    {
        IDictionary<string, string> FetchResourceProperties(string resourcePath);
    }
}
