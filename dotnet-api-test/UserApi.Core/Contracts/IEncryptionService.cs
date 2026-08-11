namespace UserApi.Core.Contracts
{
    /// <summary>
    /// Contract for symmetric encryption of sensitive data.
    /// </summary>
    public interface IEncryptionService
    {
        string Encrypt(string plainText);
        string Decrypt(string cipherText);
    }
}
