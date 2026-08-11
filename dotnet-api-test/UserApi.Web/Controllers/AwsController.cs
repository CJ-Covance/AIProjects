using System.Collections.Generic;
using System.Web.Http;
using UserApi.Core.Contracts;

namespace UserApi.Web.Controllers
{
    /// <summary>
    /// Exposes AWS API proxy endpoint returning flattened property/value pairs for client UI binding.
    /// </summary>
    [RoutePrefix("api/aws")]
    public class AwsController : ApiController
    {
        private readonly IAwsApiService _awsApiService;
        private readonly ILoggerService _logger;

        public AwsController(IAwsApiService awsApiService, ILoggerService logger)
        {
            _awsApiService = awsApiService;
            _logger = logger;
            _logger.Info("AwsController constructed.");
        }

        /// <summary>
        /// GET api/aws?path=users/123 — calls configured AWS API and returns key/value properties.
        /// </summary>
        [HttpGet]
        [Route("")]
        public IHttpActionResult GetAwsResource([FromUri] string path)
        {
            _logger.Info(string.Format("GET /api/aws invoked. Path={0}", path ?? "(root)"));
            IDictionary<string, string> properties = _awsApiService.FetchResourceProperties(path);
            _logger.Info(string.Format("GET /api/aws completed. PropertyCount={0}.", properties.Count));
            return Ok(properties);
        }
    }
}
