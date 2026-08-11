using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Web.Script.Serialization;
using UserApi.Core.Contracts;
using UserApi.Infrastructure.Base;
using UserApi.Infrastructure.Helpers;

namespace UserApi.Infrastructure.Services
{
    /// <summary>
    /// Calls AWS API Gateway / REST endpoints and flattens JSON responses into property/value pairs for UI display.
    /// Supports x-api-key authentication configured in App.config/Web.config.
    /// </summary>
    public sealed class AwsApiService : BaseService, IAwsApiService
    {
        private readonly JavaScriptSerializer _serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };

        public AwsApiService() : base("AwsApiService")
        {
        }

        /// <inheritdoc />
        public IDictionary<string, string> FetchResourceProperties(string resourcePath)
        {
            Logger.Info(string.Format("FetchResourceProperties started. Path={0}", resourcePath ?? "(root)"));
            var url = ConfigHelper.BuildAwsApiUrl(resourcePath);
            var apiKey = ConfigHelper.GetAppSetting("AwsApiKey", string.Empty);
            var region = ConfigHelper.GetAppSetting("AwsRegion", "us-east-1");

            var request = (HttpWebRequest)WebRequest.Create(url);
            request.Method = "GET";
            request.Accept = "application/json";
            request.Headers["x-amz-region"] = region;

            if (!string.IsNullOrWhiteSpace(apiKey))
            {
                request.Headers["x-api-key"] = apiKey;
                Logger.Debug("AWS API key header applied.");
            }

            try
            {
                Logger.Info(string.Format("Sending GET request to AWS API: {0}", url));
                using (var response = (HttpWebResponse)request.GetResponse())
                using (var reader = new StreamReader(response.GetResponseStream()))
                {
                    var json = reader.ReadToEnd();
                    Logger.Info(string.Format("AWS API response received. Status={0}, Length={1}.", response.StatusCode, json.Length));
                    var properties = FlattenJson(json);
                    Logger.Info(string.Format("FetchResourceProperties completed. PropertyCount={0}.", properties.Count));
                    return properties;
                }
            }
            catch (WebException webEx)
            {
                var errorBody = ReadErrorBody(webEx);
                Logger.Error(string.Format("AWS API call failed: {0}", errorBody), webEx);
                throw new InvalidOperationException("AWS API call failed: " + errorBody, webEx);
            }
        }

        private IDictionary<string, string> FlattenJson(string json)
        {
            Logger.Debug("Flattening AWS JSON response.");
            var properties = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (string.IsNullOrWhiteSpace(json))
            {
                properties["(empty)"] = string.Empty;
                return properties;
            }

            var root = _serializer.DeserializeObject(json);
            FlattenObject(string.Empty, root, properties);
            return properties;
        }

        private void FlattenObject(string prefix, object value, IDictionary<string, string> target)
        {
            if (value == null)
            {
                target[prefix.Length == 0 ? "(null)" : prefix] = string.Empty;
                return;
            }

            if (value is string || value is bool || value is int || value is long || value is decimal || value is double || value is float)
            {
                target[prefix.Length == 0 ? "value" : prefix] = Convert.ToString(value);
                return;
            }

            var dictionary = value as Dictionary<string, object>;
            if (dictionary != null)
            {
                foreach (var pair in dictionary)
                {
                    var key = string.IsNullOrEmpty(prefix) ? pair.Key : prefix + "." + pair.Key;
                    FlattenObject(key, pair.Value, target);
                }

                return;
            }

            var list = value as System.Collections.ArrayList;
            if (list != null)
            {
                for (var i = 0; i < list.Count; i++)
                {
                    var key = string.IsNullOrEmpty(prefix) ? "[" + i + "]" : prefix + "[" + i + "]";
                    FlattenObject(key, list[i], target);
                }

                return;
            }

            target[prefix.Length == 0 ? "value" : prefix] = value.ToString();
        }

        private static string ReadErrorBody(WebException exception)
        {
            if (exception.Response == null)
            {
                return exception.Message;
            }

            using (var stream = exception.Response.GetResponseStream())
            using (var reader = new StreamReader(stream))
            {
                return reader.ReadToEnd();
            }
        }
    }
}
