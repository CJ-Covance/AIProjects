using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using UserApi.Core.Contracts;
using UserApi.Core.Models;
using UserApi.Infrastructure.Base;

namespace UserApi.Infrastructure.Repositories
{
    /// <summary>
    /// Thread-safe in-memory user repository for demonstration and local testing.
    /// Replace with EF/SQL implementation in production using the configured connection string.
    /// </summary>
    public sealed class UserRepository : BaseRepository, IUserRepository
    {
        private static readonly ConcurrentDictionary<int, User> Store = new ConcurrentDictionary<int, User>();
        private static int _nextId;

        public UserRepository() : base("UserRepository")
        {
        }

        public User GetById(int id)
        {
            Logger.Info(string.Format("GetById started for user {0}.", id));
            ValidateId(id);
            User user;
            Store.TryGetValue(id, out user);
            Logger.Info(user == null
                ? string.Format("GetById completed: user {0} not found.", id)
                : string.Format("GetById completed: user {0} found.", id));
            return user;
        }

        public IEnumerable<User> GetAll()
        {
            Logger.Info("GetAll started.");
            var users = Store.Values.OrderBy(u => u.Id).ToList();
            Logger.Info(string.Format("GetAll completed. Count={0}.", users.Count));
            return users;
        }

        public User Add(User user)
        {
            Logger.Info("Add started.");
            if (user == null)
            {
                throw new System.ArgumentNullException("user");
            }

            var id = System.Threading.Interlocked.Increment(ref _nextId);
            user.Id = id;
            user.CreatedAtUtc = System.DateTime.UtcNow;
            Store[id] = user;
            Logger.Info(string.Format("Add completed. New user id={0}.", id));
            return user;
        }

        public bool Update(User user)
        {
            Logger.Info(string.Format("Update started for user {0}.", user == null ? 0 : user.Id));
            if (user == null)
            {
                throw new System.ArgumentNullException("user");
            }

            ValidateId(user.Id);
            if (!Store.ContainsKey(user.Id))
            {
                Logger.Warn(string.Format("Update failed: user {0} not found.", user.Id));
                return false;
            }

            user.UpdatedAtUtc = System.DateTime.UtcNow;
            Store[user.Id] = user;
            Logger.Info(string.Format("Update completed for user {0}.", user.Id));
            return true;
        }

        public bool Delete(int id)
        {
            Logger.Info(string.Format("Delete started for user {0}.", id));
            ValidateId(id);
            User removed;
            var success = Store.TryRemove(id, out removed);
            Logger.Info(success
                ? string.Format("Delete completed for user {0}.", id)
                : string.Format("Delete failed: user {0} not found.", id));
            return success;
        }
    }
}
