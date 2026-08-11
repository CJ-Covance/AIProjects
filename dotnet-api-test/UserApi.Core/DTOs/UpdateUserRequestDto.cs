namespace UserApi.Core.DTOs
{
    /// <summary>
    /// Request payload for updating an existing user.
    /// </summary>
    public class UpdateUserRequestDto
    {
        public string Username { get; set; }
        public string Email { get; set; }
        public string Phone { get; set; }
        public string FullName { get; set; }
    }
}
