using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Web.Script.Serialization;
using ApiTestConsole.Helpers;
using UserApi.Core.DTOs;
using UserApi.Infrastructure.Helpers;

namespace ApiTestConsole.Clients
{
    /// <summary>
    /// HTTP client for exercising the local User Web API endpoints.
    /// </summary>
    public sealed class UserApiClient
    {
        private readonly HttpClient _httpClient;
        private readonly UiLogger _logger;
        private readonly JavaScriptSerializer _serializer = new JavaScriptSerializer();

        public UserApiClient(UiLogger logger)
        {
            _logger = logger ?? throw new ArgumentNullException("logger");
            var baseUrl = ConfigHelper.GetRequiredAppSetting("UserApiBaseUrl").TrimEnd('/');
            _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl + "/") };
            _logger.Info(string.Format("UserApiClient initialized. BaseUrl={0}", baseUrl));
        }

        public UserResponseDto CreateUser(CreateUserRequestDto request)
        {
            _logger.Info("Step: POST /users — creating user.");
            var json = _serializer.Serialize(request);
            var response = _httpClient.PostAsync(
                "users",
                new StringContent(json, Encoding.UTF8, "application/json")).Result;
            EnsureSuccess(response, "Create user");
            var body = response.Content.ReadAsStringAsync().Result;
            _logger.Info("Step: POST /users — completed successfully.");
            return _serializer.Deserialize<UserResponseDto>(body);
        }

        public UserResponseDto GetUser(int id)
        {
            _logger.Info(string.Format("Step: GET /users/{0}.", id));
            var response = _httpClient.GetAsync("users/" + id).Result;
            EnsureSuccess(response, "Get user");
            var body = response.Content.ReadAsStringAsync().Result;
            _logger.Info("Step: GET /users — completed successfully.");
            return _serializer.Deserialize<UserResponseDto>(body);
        }

        public IList<UserResponseDto> GetAllUsers()
        {
            _logger.Info("Step: GET /users.");
            var response = _httpClient.GetAsync("users").Result;
            EnsureSuccess(response, "Get all users");
            var body = response.Content.ReadAsStringAsync().Result;
            _logger.Info("Step: GET /users — completed successfully.");
            return _serializer.Deserialize<IList<UserResponseDto>>(body);
        }

        public UserResponseDto UpdateUser(int id, UpdateUserRequestDto request)
        {
            _logger.Info(string.Format("Step: PUT /users/{0}.", id));
            var json = _serializer.Serialize(request);
            var response = _httpClient.PutAsync(
                "users/" + id,
                new StringContent(json, Encoding.UTF8, "application/json")).Result;
            EnsureSuccess(response, "Update user");
            var body = response.Content.ReadAsStringAsync().Result;
            _logger.Info("Step: PUT /users — completed successfully.");
            return _serializer.Deserialize<UserResponseDto>(body);
        }

        public void DeleteUser(int id)
        {
            _logger.Info(string.Format("Step: DELETE /users/{0}.", id));
            var response = _httpClient.DeleteAsync("users/" + id).Result;
            EnsureSuccess(response, "Delete user");
            _logger.Info("Step: DELETE /users — completed successfully.");
        }

        private void EnsureSuccess(HttpResponseMessage response, string operation)
        {
            if (response.IsSuccessStatusCode)
            {
                return;
            }

            var error = response.Content.ReadAsStringAsync().Result;
            _logger.Error(string.Format("{0} failed. Status={1}. Body={2}", operation, response.StatusCode, error));
            throw new InvalidOperationException(string.Format("{0} failed: {1}", operation, error));
        }
    }
}
