using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UserApi.Core.Contracts;
using UserApi.Infrastructure.Helpers;
using UserApi.Infrastructure.Logging;

namespace UserApi.Infrastructure.Security
{
    /// <summary>
    /// AES-256 encryption utility. Keys are loaded from configuration — never hardcoded.
    /// Cipher format: Base64(IV + ciphertext).
    /// </summary>
    public sealed class AesEncryptionService : IEncryptionService
    {
        private readonly byte[] _keyBytes;
        private readonly FileLoggerService _logger;

        public AesEncryptionService()
        {
            _logger = new FileLoggerService("AesEncryptionService");
            _logger.Info("Initializing AES encryption service.");
            _keyBytes = ResolveKeyBytes();
            _logger.Info("AES encryption service initialized successfully.");
        }

        /// <inheritdoc />
        public string Encrypt(string plainText)
        {
            _logger.Debug("Encrypt invoked.");
            if (plainText == null)
            {
                return null;
            }

            if (plainText.Length == 0)
            {
                return string.Empty;
            }

            using (var aes = CreateAlgorithm())
            using (var encryptor = aes.CreateEncryptor(_keyBytes, aes.IV))
            using (var ms = new MemoryStream())
            {
                ms.Write(aes.IV, 0, aes.IV.Length);
                using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
                using (var sw = new StreamWriter(cs, Encoding.UTF8))
                {
                    sw.Write(plainText);
                }

                _logger.Debug("Encrypt completed.");
                return Convert.ToBase64String(ms.ToArray());
            }
        }

        /// <inheritdoc />
        public string Decrypt(string cipherText)
        {
            _logger.Debug("Decrypt invoked.");
            if (cipherText == null)
            {
                return null;
            }

            if (cipherText.Length == 0)
            {
                return string.Empty;
            }

            var fullCipher = Convert.FromBase64String(cipherText);
            using (var aes = CreateAlgorithm())
            {
                var iv = new byte[aes.BlockSize / 8];
                Array.Copy(fullCipher, 0, iv, 0, iv.Length);
                aes.IV = iv;

                var cipherBytes = new byte[fullCipher.Length - iv.Length];
                Array.Copy(fullCipher, iv.Length, cipherBytes, 0, cipherBytes.Length);

                using (var decryptor = aes.CreateDecryptor(_keyBytes, aes.IV))
                using (var ms = new MemoryStream(cipherBytes))
                using (var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read))
                using (var sr = new StreamReader(cs, Encoding.UTF8))
                {
                    var plain = sr.ReadToEnd();
                    _logger.Debug("Decrypt completed.");
                    return plain;
                }
            }
        }

        private static Aes CreateAlgorithm()
        {
            var aes = Aes.Create();
            aes.KeySize = 256;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
            return aes;
        }

        private byte[] ResolveKeyBytes()
        {
            _logger.Debug("Resolving encryption key from configuration.");
            var configuredKey = ConfigHelper.GetRequiredAppSetting("EncryptionKey");
            using (var sha = SHA256.Create())
            {
                return sha.ComputeHash(Encoding.UTF8.GetBytes(configuredKey));
            }
        }
    }
}
