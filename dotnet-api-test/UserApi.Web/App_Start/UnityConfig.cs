using System.Web.Http;
using Unity;
using Unity.WebApi;
using UserApi.Core.Contracts;
using UserApi.Infrastructure.Repositories;
using UserApi.Infrastructure.Security;
using UserApi.Infrastructure.Services;

namespace UserApi.Web.App_Start
{
    /// <summary>
    /// Unity container registration — interface-based dependency injection (polymorphism).
    /// </summary>
    public static class UnityConfig
    {
        public static void RegisterComponents()
        {
            var container = new UnityContainer();

            container.RegisterType<ILoggerService, Infrastructure.Logging.FileLoggerService>();
            container.RegisterType<IEncryptionService, AesEncryptionService>(new Unity.Lifetime.ContainerControlledLifetimeManager());
            container.RegisterType<IUserRepository, UserRepository>(new Unity.Lifetime.ContainerControlledLifetimeManager());
            container.RegisterType<IUserService, UserService>();
            container.RegisterType<IAwsApiService, AwsApiService>();

            GlobalConfiguration.Configuration.DependencyResolver = new UnityDependencyResolver(container);
        }
    }
}
