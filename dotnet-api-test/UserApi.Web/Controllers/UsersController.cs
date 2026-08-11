using System.Collections.Generic;
using System.Net;
using System.Web.Http;
using UserApi.Core.Contracts;
using UserApi.Core.DTOs;

namespace UserApi.Web.Controllers
{
    /// <summary>
    /// REST controller for user CRUD operations. Depends on IUserService abstraction only.
    /// </summary>
    [RoutePrefix("api/users")]
    public class UsersController : ApiController
    {
        private readonly IUserService _userService;
        private readonly ILoggerService _logger;

        public UsersController(IUserService userService, ILoggerService logger)
        {
            _userService = userService;
            _logger = logger;
            _logger.Info("UsersController constructed.");
        }

        /// <summary>POST api/users — create user with encrypted sensitive fields.</summary>
        [HttpPost]
        [Route("")]
        public IHttpActionResult CreateUser([FromBody] CreateUserRequestDto request)
        {
            _logger.Info("POST /api/users invoked.");
            var created = _userService.CreateUser(request);
            _logger.Info(string.Format("POST /api/users completed. UserId={0}.", created.Id));
            return Content(HttpStatusCode.Created, created);
        }

        /// <summary>GET api/users/{id} — fetch user with decrypted sensitive fields.</summary>
        [HttpGet]
        [Route("{id:int}")]
        public IHttpActionResult GetUser(int id)
        {
            _logger.Info(string.Format("GET /api/users/{0} invoked.", id));
            var user = _userService.GetUser(id);
            if (user == null)
            {
                _logger.Warn(string.Format("GET /api/users/{0} — not found.", id));
                return NotFound();
            }

            _logger.Info(string.Format("GET /api/users/{0} completed.", id));
            return Ok(user);
        }

        /// <summary>GET api/users — list all users.</summary>
        [HttpGet]
        [Route("")]
        public IHttpActionResult GetAllUsers()
        {
            _logger.Info("GET /api/users invoked.");
            IEnumerable<UserResponseDto> users = _userService.GetAllUsers();
            _logger.Info("GET /api/users completed.");
            return Ok(users);
        }

        /// <summary>PUT api/users/{id} — update user.</summary>
        [HttpPut]
        [Route("{id:int}")]
        public IHttpActionResult UpdateUser(int id, [FromBody] UpdateUserRequestDto request)
        {
            _logger.Info(string.Format("PUT /api/users/{0} invoked.", id));
            var updated = _userService.UpdateUser(id, request);
            if (updated == null)
            {
                _logger.Warn(string.Format("PUT /api/users/{0} — not found.", id));
                return NotFound();
            }

            _logger.Info(string.Format("PUT /api/users/{0} completed.", id));
            return Ok(updated);
        }

        /// <summary>DELETE api/users/{id} — remove user.</summary>
        [HttpDelete]
        [Route("{id:int}")]
        public IHttpActionResult DeleteUser(int id)
        {
            _logger.Info(string.Format("DELETE /api/users/{0} invoked.", id));
            if (!_userService.DeleteUser(id))
            {
                _logger.Warn(string.Format("DELETE /api/users/{0} — not found.", id));
                return NotFound();
            }

            _logger.Info(string.Format("DELETE /api/users/{0} completed.", id));
            return StatusCode(HttpStatusCode.NoContent);
        }
    }
}
