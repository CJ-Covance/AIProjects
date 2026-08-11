using System.Collections.Generic;
using UserApi.Core.DTOs;

namespace UserApi.Core.Contracts
{
    /// <summary>
    /// Application service contract for user operations.
    /// </summary>
    public interface IUserService
    {
        UserResponseDto CreateUser(CreateUserRequestDto request);
        UserResponseDto GetUser(int id);
        IEnumerable<UserResponseDto> GetAllUsers();
        UserResponseDto UpdateUser(int id, UpdateUserRequestDto request);
        bool DeleteUser(int id);
    }
}
