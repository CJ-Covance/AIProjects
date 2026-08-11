using System;

namespace UserApi.Core.DTOs
{
    /// <summary>
    /// Safe outward-facing representation of a user with decrypted sensitive fields.
    /// </summary>
    public class UserResponseDto
    {
        public int Id { get; set; }
        public string Username { get; set; }
        public string Email { get; set; }
        public string Phone { get; set; }
        public string FullName { get; set; }
        public DateTime CreatedAtUtc { get; set; }
        public DateTime? UpdatedAtUtc { get; set; }
    }
}
