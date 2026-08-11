using UserApi.Core.Contracts;
using UserApi.Infrastructure.Helpers;
using UserApi.Infrastructure.Logging;

namespace UserApi.Infrastructure.Base
{
    /// <summary>
    /// Base service providing logging and shared validation for derived services.
    /// </summary>
    public abstract class BaseService
    {
        protected readonly ILoggerService Logger;

        protected BaseService(string componentName)
        {
            Logger = new FileLoggerService(componentName);
            Logger.Info(string.Format("{0} service initialized.", componentName));
        }

        /// <summary>
        /// Validates create/update DTO fields common to user operations.
        /// </summary>
        protected virtual void ValidateUserFields(string username, string email, string phone, string fullName)
        {
            Logger.Debug("Validating user fields.");
            ValidationHelper.ValidateUsername(username);
            ValidationHelper.ValidateEmail(email);
            ValidationHelper.ValidatePhone(phone);
            ValidationHelper.RequireNotNullOrWhiteSpace(fullName, "FullName");
        }
    }
}
