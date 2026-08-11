using System;

namespace UserApi.Core.Models
{
    /// <summary>
    /// Domain entity representing an application user.
    /// Sensitive fields are stored encrypted at rest.
    /// </summary>
    public class User
    {
        private int _id;
        private string _username;
        private string _emailEncrypted;
        private string _phoneEncrypted;
        private string _fullName;
        private DateTime _createdAtUtc;
        private DateTime? _updatedAtUtc;

        /// <summary>Gets or sets the unique identifier.</summary>
        public int Id
        {
            get { return _id; }
            set { _id = value; }
        }

        /// <summary>Gets or sets the public username.</summary>
        public string Username
        {
            get { return _username; }
            set { _username = value; }
        }

        /// <summary>Gets or sets the encrypted email payload.</summary>
        public string EmailEncrypted
        {
            get { return _emailEncrypted; }
            set { _emailEncrypted = value; }
        }

        /// <summary>Gets or sets the encrypted phone payload.</summary>
        public string PhoneEncrypted
        {
            get { return _phoneEncrypted; }
            set { _phoneEncrypted = value; }
        }

        /// <summary>Gets or sets the user's display name.</summary>
        public string FullName
        {
            get { return _fullName; }
            set { _fullName = value; }
        }

        /// <summary>Gets or sets the UTC creation timestamp.</summary>
        public DateTime CreatedAtUtc
        {
            get { return _createdAtUtc; }
            set { _createdAtUtc = value; }
        }

        /// <summary>Gets or sets the UTC last-update timestamp.</summary>
        public DateTime? UpdatedAtUtc
        {
            get { return _updatedAtUtc; }
            set { _updatedAtUtc = value; }
        }
    }
}
