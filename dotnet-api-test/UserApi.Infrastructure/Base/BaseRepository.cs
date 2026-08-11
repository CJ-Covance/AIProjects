using UserApi.Core.Contracts;
using UserApi.Infrastructure.Logging;

namespace UserApi.Infrastructure.Base
{
    /// <summary>
    /// Base repository providing shared logging and validation hooks.
    /// Demonstrates inheritance and template-method style extension points.
    /// </summary>
    public abstract class BaseRepository
    {
        protected readonly ILoggerService Logger;

        protected BaseRepository(string componentName)
        {
            Logger = new FileLoggerService(componentName);
            Logger.Info(string.Format("{0} repository initialized.", componentName));
        }

        /// <summary>
        /// Validates an entity identifier before data access operations.
        /// </summary>
        protected virtual void ValidateId(int id)
        {
            Logger.Debug(string.Format("Validating identifier: {0}", id));
            if (id <= 0)
            {
                Logger.Warn(string.Format("Invalid identifier supplied: {0}", id));
                throw new System.ArgumentOutOfRangeException("id", "Identifier must be greater than zero.");
            }
        }
    }
}
