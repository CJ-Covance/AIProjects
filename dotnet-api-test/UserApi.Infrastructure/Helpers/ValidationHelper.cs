using System;
using System.Net.Mail;
using System.Text.RegularExpressions;

namespace UserApi.Infrastructure.Helpers
{
    /// <summary>
    /// Shared validation routines used by services before persistence.
    /// </summary>
    public static class ValidationHelper
    {
        private static readonly Regex UsernamePattern = new Regex(@"^[a-zA-Z0-9_]{3,50}$", RegexOptions.Compiled);

        public static void RequireNotNullOrWhiteSpace(string value, string fieldName)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                throw new ArgumentException(string.Format("{0} is required.", fieldName), fieldName);
            }
        }

        public static void ValidateUsername(string username)
        {
            RequireNotNullOrWhiteSpace(username, "Username");
            if (!UsernamePattern.IsMatch(username))
            {
                throw new ArgumentException("Username must be 3-50 characters and contain only letters, numbers, or underscore.", "Username");
            }
        }

        public static void ValidateEmail(string email)
        {
            RequireNotNullOrWhiteSpace(email, "Email");
            try
            {
                var address = new MailAddress(email);
                if (!string.Equals(address.Address, email, StringComparison.OrdinalIgnoreCase))
                {
                    throw new ArgumentException("Email format is invalid.", "Email");
                }
            }
            catch (FormatException)
            {
                throw new ArgumentException("Email format is invalid.", "Email");
            }
        }

        public static void ValidatePhone(string phone)
        {
            RequireNotNullOrWhiteSpace(phone, "Phone");
            if (phone.Length < 7 || phone.Length > 20)
            {
                throw new ArgumentException("Phone must be between 7 and 20 characters.", "Phone");
            }
        }
    }
}
