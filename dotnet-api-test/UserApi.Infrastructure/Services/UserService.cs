using System;
using System.Collections.Generic;
using System.Linq;
using UserApi.Core.Contracts;
using UserApi.Core.DTOs;
using UserApi.Core.Models;
using UserApi.Infrastructure.Base;

namespace UserApi.Infrastructure.Services
{
    /// <summary>
    /// User application service with encryption of sensitive fields and DTO mapping.
    /// </summary>
    public sealed class UserService : BaseService, IUserService
    {
        private readonly IUserRepository _userRepository;
        private readonly IEncryptionService _encryptionService;

        public UserService(IUserRepository userRepository, IEncryptionService encryptionService)
            : base("UserService")
        {
            _userRepository = userRepository ?? throw new ArgumentNullException("userRepository");
            _encryptionService = encryptionService ?? throw new ArgumentNullException("encryptionService");
        }

        public UserResponseDto CreateUser(CreateUserRequestDto request)
        {
            Logger.Info("CreateUser started.");
            if (request == null)
            {
                throw new ArgumentNullException("request");
            }

            ValidateUserFields(request.Username, request.Email, request.Phone, request.FullName);

            var entity = new User
            {
                Username = request.Username.Trim(),
                FullName = request.FullName.Trim(),
                EmailEncrypted = _encryptionService.Encrypt(request.Email.Trim()),
                PhoneEncrypted = _encryptionService.Encrypt(request.Phone.Trim())
            };

            var created = _userRepository.Add(entity);
            Logger.Info(string.Format("CreateUser completed. UserId={0}.", created.Id));
            return MapToDto(created);
        }

        public UserResponseDto GetUser(int id)
        {
            Logger.Info(string.Format("GetUser started. UserId={0}.", id));
            var user = _userRepository.GetById(id);
            if (user == null)
            {
                Logger.Warn(string.Format("GetUser: user {0} not found.", id));
                return null;
            }

            Logger.Info(string.Format("GetUser completed. UserId={0}.", id));
            return MapToDto(user);
        }

        public IEnumerable<UserResponseDto> GetAllUsers()
        {
            Logger.Info("GetAllUsers started.");
            var result = _userRepository.GetAll().Select(MapToDto).ToList();
            Logger.Info(string.Format("GetAllUsers completed. Count={0}.", result.Count));
            return result;
        }

        public UserResponseDto UpdateUser(int id, UpdateUserRequestDto request)
        {
            Logger.Info(string.Format("UpdateUser started. UserId={0}.", id));
            if (request == null)
            {
                throw new ArgumentNullException("request");
            }

            ValidateUserFields(request.Username, request.Email, request.Phone, request.FullName);

            var existing = _userRepository.GetById(id);
            if (existing == null)
            {
                Logger.Warn(string.Format("UpdateUser: user {0} not found.", id));
                return null;
            }

            existing.Username = request.Username.Trim();
            existing.FullName = request.FullName.Trim();
            existing.EmailEncrypted = _encryptionService.Encrypt(request.Email.Trim());
            existing.PhoneEncrypted = _encryptionService.Encrypt(request.Phone.Trim());

            if (!_userRepository.Update(existing))
            {
                Logger.Warn(string.Format("UpdateUser failed for user {0}.", id));
                return null;
            }

            Logger.Info(string.Format("UpdateUser completed. UserId={0}.", id));
            return MapToDto(existing);
        }

        public bool DeleteUser(int id)
        {
            Logger.Info(string.Format("DeleteUser started. UserId={0}.", id));
            var deleted = _userRepository.Delete(id);
            Logger.Info(string.Format("DeleteUser completed. Success={0}.", deleted));
            return deleted;
        }

        /// <summary>
        /// Polymorphic mapping hook — derived services may override to customize outward DTO shape.
        /// </summary>
        protected virtual UserResponseDto MapToDto(User user)
        {
            return new UserResponseDto
            {
                Id = user.Id,
                Username = user.Username,
                FullName = user.FullName,
                Email = _encryptionService.Decrypt(user.EmailEncrypted),
                Phone = _encryptionService.Decrypt(user.PhoneEncrypted),
                CreatedAtUtc = user.CreatedAtUtc,
                UpdatedAtUtc = user.UpdatedAtUtc
            };
        }
    }
}
