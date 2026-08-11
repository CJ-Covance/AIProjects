namespace UserApi.Core.Contracts
{
    /// <summary>
    /// Abstraction for structured application logging.
    /// </summary>
    public interface ILoggerService
    {
        void Info(string message);
        void Warn(string message);
        void Error(string message, System.Exception exception = null);
        void Debug(string message);
    }
}
