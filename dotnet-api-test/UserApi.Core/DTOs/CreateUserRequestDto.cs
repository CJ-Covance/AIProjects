namespace UserApi.Core.DTOs
{
    /// <summary>
    /// Request payload for creating a user. Plain-text sensitive fields are encrypted by the service layer.
    /// </summary>
    public class CreateUserRequestDto
    {
        public string Username { get; set; }
        public string Email { get; set; }
        public string Phone { get; set; }
        public string FullName { get; set; }
    }
}
