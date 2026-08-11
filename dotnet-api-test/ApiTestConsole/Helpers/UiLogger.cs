using System;
using System.Windows.Forms;

namespace ApiTestConsole.Helpers
{
    /// <summary>
    /// Bridges infrastructure logging to the WinForms log panel for step-by-step monitoring.
    /// </summary>
    public sealed class UiLogger
    {
        private readonly TextBox _logTextBox;

        public UiLogger(TextBox logTextBox)
        {
            _logTextBox = logTextBox ?? throw new ArgumentNullException("logTextBox");
        }

        public void Info(string message)
        {
            Write("INFO", message);
        }

        public void Warn(string message)
        {
            Write("WARN", message);
        }

        public void Error(string message, Exception exception = null)
        {
            var details = exception == null ? message : message + " | " + exception.Message;
            Write("ERROR", details);
        }

        private void Write(string level, string message)
        {
            if (_logTextBox.InvokeRequired)
            {
                _logTextBox.Invoke(new Action<string, string>(Write), level, message);
                return;
            }

            _logTextBox.AppendText(string.Format(
                "{0:HH:mm:ss.fff} [{1}] {2}{3}",
                DateTime.Now,
                level,
                message,
                Environment.NewLine));
            _logTextBox.SelectionStart = _logTextBox.TextLength;
            _logTextBox.ScrollToCaret();
        }
    }
}
