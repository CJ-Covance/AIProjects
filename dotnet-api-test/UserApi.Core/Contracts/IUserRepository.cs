using System.Collections.Generic;
using UserApi.Core.Models;

namespace UserApi.Core.Contracts
{
    /// <summary>
    /// Repository abstraction for user persistence.
    /// </summary>
    public interface IUserRepository
    {
        User GetById(int id);
        IEnumerable<User> GetAll();
        User Add(User user);
        bool Update(User user);
        bool Delete(int id);
    }
}
