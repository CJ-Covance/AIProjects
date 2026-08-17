using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using JiraTestDataImporter.Configuration;
using JiraTestDataImporter.Logging;
using JiraTestDataImporter.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace JiraTestDataImporter.Jira
{
    public sealed class JiraClient : IJiraClient, IDisposable
    {
        public static readonly IList<string> DefaultSearchFields = new List<string>
        {
            "summary",
            "description",
            "status",
            "priority",
            "issuetype",
            "reporter",
            "assignee",
            "created",
            "updated",
            "labels",
            "components",
            "project"
        };

        private readonly HttpClient _httpClient;
        private readonly JiraSettings _settings;
        private readonly IAppLogger _logger;
        private readonly int _maxRetryAttempts = 3;

        public JiraClient(JiraSettings settings, IAppLogger logger, HttpMessageHandler handler = null)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));

            _httpClient = handler == null ? new HttpClient() : new HttpClient(handler);
            _httpClient.BaseAddress = new Uri(NormalizeBaseUrl(_settings.BaseUrl));
            _httpClient.Timeout = TimeSpan.FromSeconds(_settings.TimeoutSeconds);
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            _httpClient.DefaultRequestHeaders.Authorization = CreateBasicAuthHeader(_settings.User, _settings.ApiToken);
        }

        public async Task<JiraConnectionTestResult> TestConnectionAsync(CancellationToken cancellationToken = default(CancellationToken))
        {
            _logger.Log(LogLevel.Information, "Testing Jira connectivity.");

            try
            {
                var projectKey = string.IsNullOrWhiteSpace(_settings.ProjectKey)
                    ? ExtractProjectKeyFromJql(_settings.Jql)
                    : _settings.ProjectKey;

                if (!string.IsNullOrWhiteSpace(projectKey))
                {
                    await GetProjectAsync(projectKey, cancellationToken).ConfigureAwait(false);
                }

                var searchResult = await SearchIssuesAsync(_settings.Jql, 0, 1, cancellationToken)
                    .ConfigureAwait(false);

                return new JiraConnectionTestResult
                {
                    IsSuccessful = true,
                    Message = "Jira connection successful.",
                    IssueCount = searchResult.Total
                };
            }
            catch (JiraApiException ex)
            {
                return new JiraConnectionTestResult
                {
                    IsSuccessful = false,
                    Message = ex.Message,
                    IssueCount = 0
                };
            }
        }

        public Task<JiraSearchResult> SearchIssuesAsync(
            string jql,
            int startAt,
            int maxResults,
            CancellationToken cancellationToken = default(CancellationToken))
        {
            var request = new JiraRequest(jql, startAt, maxResults, DefaultSearchFields);
            return ExecuteWithRetryAsync(
                () => SearchIssuesInternalAsync(request, cancellationToken),
                cancellationToken);
        }

        public async Task<IList<JiraIssue>> SearchAllIssuesAsync(
            string jql,
            int pageSize,
            CancellationToken cancellationToken = default(CancellationToken))
        {
            var allIssues = new List<JiraIssue>();
            var startAt = 0;
            JiraSearchResult page;

            _logger.Log(LogLevel.Information, $"Executing JQL: {jql}");

            do
            {
                page = await SearchIssuesAsync(jql, startAt, pageSize, cancellationToken).ConfigureAwait(false);
                allIssues.AddRange(page.Issues);
                startAt += page.Issues.Count;

                _logger.Log(
                    LogLevel.Debug,
                    $"Retrieved page starting at {page.StartAt}. Batch size: {page.Issues.Count}. Total so far: {allIssues.Count}/{page.Total}.");
            }
            while (page.HasMore && page.Issues.Count > 0);

            _logger.Log(LogLevel.Information, $"Jira returned {allIssues.Count} issue(s).");
            return allIssues;
        }

        public Task<JiraIssue> GetIssueAsync(string issueKey, CancellationToken cancellationToken = default(CancellationToken))
        {
            if (string.IsNullOrWhiteSpace(issueKey))
            {
                throw new ArgumentException("Issue key is required.", nameof(issueKey));
            }

            var relativeUrl = $"rest/api/{_settings.ApiVersion}/issue/{Uri.EscapeDataString(issueKey)}?fields={BuildFieldsQuery()}";
            return ExecuteWithRetryAsync(
                async () =>
                {
                    var response = await SendAsync(HttpMethod.Get, relativeUrl, null, cancellationToken)
                        .ConfigureAwait(false);
                    var json = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                    return JiraIssueParser.ParseIssue(JObject.Parse(json));
                },
                cancellationToken);
        }

        public Task<JiraProject> GetProjectAsync(string projectKey, CancellationToken cancellationToken = default(CancellationToken))
        {
            if (string.IsNullOrWhiteSpace(projectKey))
            {
                throw new ArgumentException("Project key is required.", nameof(projectKey));
            }

            var relativeUrl = $"rest/api/{_settings.ApiVersion}/project/{Uri.EscapeDataString(projectKey)}";
            return ExecuteWithRetryAsync(
                async () =>
                {
                    var response = await SendAsync(HttpMethod.Get, relativeUrl, null, cancellationToken)
                        .ConfigureAwait(false);
                    var json = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                    var token = JObject.Parse(json);

                    return new JiraProject
                    {
                        Id = token.Value<string>("id"),
                        Key = token.Value<string>("key"),
                        Name = token.Value<string>("name")
                    };
                },
                cancellationToken);
        }

        public void Dispose()
        {
            _httpClient.Dispose();
        }

        internal async Task<JiraSearchResult> SearchIssuesInternalAsync(
            JiraRequest request,
            CancellationToken cancellationToken)
        {
            var relativeUrl = $"rest/api/{_settings.ApiVersion}/search";
            var payload = new
            {
                jql = request.Jql,
                startAt = request.StartAt,
                maxResults = request.MaxResults,
                fields = request.Fields
            };

            var response = await SendAsync(
                    HttpMethod.Post,
                    relativeUrl,
                    JsonConvert.SerializeObject(payload),
                    cancellationToken)
                .ConfigureAwait(false);

            var json = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var token = JObject.Parse(json);
            var issuesToken = token["issues"] as JArray ?? new JArray();

            var result = new JiraSearchResult
            {
                StartAt = token.Value<int?>("startAt") ?? request.StartAt,
                MaxResults = token.Value<int?>("maxResults") ?? request.MaxResults,
                Total = token.Value<int?>("total") ?? issuesToken.Count,
                Issues = issuesToken.Select(JiraIssueParser.ParseIssue).ToList()
            };

            return result;
        }

        private async Task<HttpResponseMessage> SendAsync(
            HttpMethod method,
            string relativeUrl,
            string jsonBody,
            CancellationToken cancellationToken)
        {
            using (var request = new HttpRequestMessage(method, relativeUrl))
            {
                if (!string.IsNullOrEmpty(jsonBody))
                {
                    request.Content = new StringContent(jsonBody, Encoding.UTF8, "application/json");
                }

                HttpResponseMessage response;
                try
                {
                    response = await _httpClient.SendAsync(request, cancellationToken).ConfigureAwait(false);
                }
                catch (TaskCanceledException ex) when (!cancellationToken.IsCancellationRequested)
                {
                    throw new JiraApiException("Jira request timed out.", HttpStatusCode.RequestTimeout, ex);
                }
                catch (HttpRequestException ex)
                {
                    throw new JiraApiException("Unable to reach Jira.", null, ex);
                }

                if (response.IsSuccessStatusCode)
                {
                    return response;
                }

                var body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                throw CreateApiException(response.StatusCode, body, relativeUrl);
            }
        }

        private async Task<T> ExecuteWithRetryAsync<T>(
            Func<Task<T>> operation,
            CancellationToken cancellationToken)
        {
            var attempt = 0;
            while (true)
            {
                attempt++;
                try
                {
                    return await operation().ConfigureAwait(false);
                }
                catch (JiraApiException ex) when (ShouldRetry(ex) && attempt < _maxRetryAttempts)
                {
                    var delay = GetRetryDelay(ex, attempt);
                    _logger.Log(
                        LogLevel.Warning,
                        $"Transient Jira error ({ex.StatusCode}). Retrying in {delay.TotalSeconds:0} seconds. Attempt {attempt}/{_maxRetryAttempts}.");
                    await Task.Delay(delay, cancellationToken).ConfigureAwait(false);
                }
            }
        }

        private static bool ShouldRetry(JiraApiException exception)
        {
            if (exception.StatusCode == null)
            {
                return true;
            }

            var statusCode = (int)exception.StatusCode.Value;
            return statusCode == 429 || statusCode >= 500;
        }

        private static TimeSpan GetRetryDelay(JiraApiException exception, int attempt)
        {
            if (exception.RetryAfter.HasValue)
            {
                return exception.RetryAfter.Value;
            }

            return TimeSpan.FromSeconds(Math.Pow(2, attempt));
        }

        private static AuthenticationHeaderValue CreateBasicAuthHeader(string user, string apiToken)
        {
            var credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{user}:{apiToken}"));
            return new AuthenticationHeaderValue("Basic", credentials);
        }

        private static string NormalizeBaseUrl(string baseUrl)
        {
            return baseUrl.Trim().TrimEnd('/') + "/";
        }

        private static string BuildFieldsQuery()
        {
            return string.Join(",", DefaultSearchFields);
        }

        private static string ExtractProjectKeyFromJql(string jql)
        {
            if (string.IsNullOrWhiteSpace(jql))
            {
                return null;
            }

            var match = System.Text.RegularExpressions.Regex.Match(
                jql,
                @"project\s*=\s*(?<key>[A-Za-z][A-Za-z0-9_]*)",
                System.Text.RegularExpressions.RegexOptions.IgnoreCase);

            return match.Success ? match.Groups["key"].Value : null;
        }

        private static JiraApiException CreateApiException(HttpStatusCode statusCode, string body, string relativeUrl)
        {
            var sanitizedBody = string.IsNullOrWhiteSpace(body) ? string.Empty : body;
            var message = statusCode switch
            {
                HttpStatusCode.BadRequest => "Jira rejected the request. Verify the JQL query and request payload.",
                HttpStatusCode.Unauthorized => "Jira authentication failed. Verify the configured user and API token.",
                HttpStatusCode.Forbidden => "Jira authorization failed. Verify project permissions for the integration account.",
                HttpStatusCode.NotFound => $"Jira resource was not found: {relativeUrl}",
                (HttpStatusCode)429 => "Jira rate limit reached.",
                _ when (int)statusCode >= 500 => "Jira service is unavailable.",
                _ => $"Jira API request failed with status {(int)statusCode}."
            };

            return new JiraApiException(message, statusCode, null, sanitizedBody);
        }
    }

    public sealed class JiraApiException : Exception
    {
        public JiraApiException(string message, HttpStatusCode? statusCode, Exception innerException = null, string responseBody = null)
            : base(message, innerException)
        {
            StatusCode = statusCode;
            ResponseBody = responseBody;
        }

        public HttpStatusCode? StatusCode { get; }

        public string ResponseBody { get; }

        public TimeSpan? RetryAfter { get; set; }
    }
}
