using System;
using System.Net;
using System.Net.Http;
using System.Web.Http.Filters;
using UserApi.Infrastructure.Logging;

namespace UserApi.Web.Filters
{
    /// <summary>
    /// Global exception handler returning consistent API error responses.
    /// </summary>
    public sealed class GlobalExceptionFilter : ExceptionFilterAttribute
    {
        private static readonly FileLoggerService Logger = new FileLoggerService("GlobalExceptionFilter");

        public override void OnException(HttpActionExecutedContext context)
        {
            Logger.Error("Unhandled API exception.", context.Exception);

            if (context.Exception is ArgumentException)
            {
                context.Response = context.Request.CreateErrorResponse(HttpStatusCode.BadRequest, context.Exception.Message);
                return;
            }

            if (context.Exception is UnauthorizedAccessException)
            {
                context.Response = context.Request.CreateErrorResponse(HttpStatusCode.Unauthorized, "Unauthorized.");
                return;
            }

            context.Response = context.Request.CreateErrorResponse(
                HttpStatusCode.InternalServerError,
                "An unexpected error occurred. Refer to server logs for details.");
        }
    }
}
