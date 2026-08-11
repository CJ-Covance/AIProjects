using System;
using System.Collections.Generic;
using ApiTestConsole.Helpers;
using UserApi.Core.Contracts;
using UserApi.Infrastructure.Services;

namespace ApiTestConsole.Clients
{
    /// <summary>
    /// Client wrapper that calls AWS API directly and returns flattened properties for UI binding.
    /// Can also be routed through the Web API proxy when preferred.
    /// </summary>
    public sealed class AwsApiClient
    {
        private readonly IAwsApiService _awsApiService;
        private readonly UiLogger _logger;

        public AwsApiClient(UiLogger logger)
        {
            _logger = logger ?? throw new ArgumentNullException("logger");
            _awsApiService = new AwsApiService();
            _logger.Info("AwsApiClient initialized.");
        }

        public IDictionary<string, string> FetchProperties(string resourcePath)
        {
            _logger.Info(string.Format("Step: Calling AWS API. Path={0}", string.IsNullOrWhiteSpace(resourcePath) ? "(root)" : resourcePath));
            var properties = _awsApiService.FetchResourceProperties(resourcePath);
            _logger.Info(string.Format("Step: AWS API call completed. PropertyCount={0}.", properties.Count));
            return properties;
        }
    }
}
