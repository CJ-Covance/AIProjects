using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using JiraTestDataImporter.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace JiraTestDataImporter.Jira
{
    public static class JiraIssueParser
    {
        public static JiraIssue ParseIssue(JToken issueToken)
        {
            if (issueToken == null)
            {
                throw new InvalidOperationException("Issue payload is missing.");
            }

            var fields = issueToken["fields"] as JObject ?? new JObject();
            return new JiraIssue
            {
                Id = issueToken.Value<string>("id"),
                Key = issueToken.Value<string>("key"),
                Summary = fields.Value<string>("summary"),
                Description = ExtractDescription(fields["description"]),
                Status = GetFieldName(fields["status"]),
                Priority = GetFieldName(fields["priority"]),
                IssueType = GetFieldName(fields["issuetype"]),
                Reporter = GetDisplayName(fields["reporter"]),
                Assignee = GetDisplayName(fields["assignee"]),
                Created = ParseJiraDate(fields.Value<string>("created")),
                Updated = ParseJiraDate(fields.Value<string>("updated")),
                Labels = fields["labels"]?.Select(label => label.Value<string>()).Where(label => !string.IsNullOrWhiteSpace(label)).ToList()
                         ?? new List<string>(),
                Components = fields["components"]?.Select(component => component["name"]?.Value<string>())
                    .Where(name => !string.IsNullOrWhiteSpace(name)).ToList()
                         ?? new List<string>(),
                ProjectKey = GetProjectKey(fields["project"])
            };
        }

        private static string GetFieldName(JToken token)
        {
            return token != null && token.Type == JTokenType.Object
                ? token["name"]?.Value<string>()
                : null;
        }

        private static string GetDisplayName(JToken token)
        {
            return token != null && token.Type == JTokenType.Object
                ? token["displayName"]?.Value<string>()
                : null;
        }

        private static string GetProjectKey(JToken token)
        {
            return token != null && token.Type == JTokenType.Object
                ? token["key"]?.Value<string>()
                : null;
        }

        public static string ExtractDescription(JToken descriptionToken)
        {
            if (descriptionToken == null || descriptionToken.Type == JTokenType.Null)
            {
                return null;
            }

            if (descriptionToken.Type == JTokenType.String)
            {
                return descriptionToken.Value<string>();
            }

            return descriptionToken.ToString(Formatting.None);
        }

        public static DateTime? ParseJiraDate(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return null;
            }

            if (DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal, out var parsed))
            {
                return parsed;
            }

            return null;
        }
    }
}
