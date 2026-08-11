namespace ApiTestConsole.Models
{
    /// <summary>
    /// Row model for property/value grid binding in the AWS response panel.
    /// </summary>
    public sealed class PropertyValueRow
    {
        public string Property { get; set; }
        public string Value { get; set; }
    }
}
