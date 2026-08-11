using System;
using System.ComponentModel;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using ApiTestConsole.Clients;
using ApiTestConsole.Helpers;
using ApiTestConsole.Models;
using UserApi.Core.DTOs;
using UserApi.Infrastructure.Helpers;

namespace ApiTestConsole
{
    /// <summary>
    /// API test console with User CRUD actions and AWS response property/value viewer.
    /// </summary>
    public partial class MainForm : Form
    {
        private readonly UiLogger _logger;
        private readonly UserApiClient _userApiClient;
        private readonly AwsApiClient _awsApiClient;
        private readonly AwsSnsClient _awsSnsClient;
        private int _lastCreatedUserId;

        public MainForm()
        {
            InitializeComponent();
            _logger = new UiLogger(txtLog);
            _userApiClient = new UserApiClient(_logger);
            _awsApiClient = new AwsApiClient(_logger);
            _awsSnsClient = new AwsSnsClient(_logger);

            txtAwsPath.Text = ConfigHelper.GetAppSetting("AwsDefaultResourcePath", string.Empty);
            LoadSnsDefaults();
            ConfigurePropertyGrid();
            _logger.Info("MainForm loaded. Ready for API testing.");
        }

        private void ConfigurePropertyGrid()
        {
            dgvAwsProperties.AutoGenerateColumns = false;
            dgvAwsProperties.Columns.Clear();
            dgvAwsProperties.Columns.Add(new DataGridViewTextBoxColumn
            {
                DataPropertyName = "Property",
                HeaderText = "Property",
                Width = 260,
                ReadOnly = true
            });
            dgvAwsProperties.Columns.Add(new DataGridViewTextBoxColumn
            {
                DataPropertyName = "Value",
                HeaderText = "Value",
                AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill,
                ReadOnly = true
            });
            dgvAwsProperties.ReadOnly = true;
            dgvAwsProperties.AllowUserToAddRows = false;
            dgvAwsProperties.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
        }

        private void LoadSnsDefaults()
        {
            txtSnsProfile.Text = ConfigHelper.GetAppSetting("AwsSnsProfileName", "labcorp-connector");
            txtSnsAccessKey.Text = ConfigHelper.GetAppSetting("AwsSnsAccessKey", string.Empty);
            txtSnsSecretKey.Text = ConfigHelper.GetAppSetting("AwsSnsSecretKey", string.Empty);
            txtSnsRegion.Text = ConfigHelper.GetAppSetting("AwsSnsRegion", "us-east-1");
            txtSnsTopicArn.Text = ConfigHelper.GetAppSetting(
                "AwsSnsTopicArn",
                "arn:aws:sns:us-east-1:763216446258:labcorpembark-receiving-topic-dev");
            txtSnsMessage.Text = ConfigHelper.GetAppSetting("AwsSnsDefaultMessage", "preflig");
        }

        private void BindSnsResult(AwsSnsPublishResult result)
        {
            propertyGridUser.SelectedObject = result;
            propertyGridUser.Refresh();

            var rows = new[]
            {
                new PropertyValueRow { Property = "MessageId", Value = result.MessageId },
                new PropertyValueRow { Property = "SequenceNumber", Value = result.SequenceNumber ?? string.Empty },
                new PropertyValueRow { Property = "HttpStatusCode", Value = result.HttpStatusCode },
                new PropertyValueRow { Property = "ProfileName", Value = result.ProfileName },
                new PropertyValueRow { Property = "Region", Value = result.Region },
                new PropertyValueRow { Property = "TopicArn", Value = result.TopicArn }
            };

            dgvAwsProperties.DataSource = new BindingList<PropertyValueRow>(rows.ToList());
        }

        private void btnCreateUser_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: Create User button clicked.");
                var request = new CreateUserRequestDto
                {
                    Username = txtUsername.Text.Trim(),
                    Email = txtEmail.Text.Trim(),
                    Phone = txtPhone.Text.Trim(),
                    FullName = txtFullName.Text.Trim()
                };

                var created = _userApiClient.CreateUser(request);
                _lastCreatedUserId = created.Id;
                txtUserId.Text = created.Id.ToString();
                BindUserResult(created);
                _logger.Info(string.Format("UI: User created successfully. Id={0}.", created.Id));
            }
            catch (Exception ex)
            {
                _logger.Error("UI: Create user failed.", ex);
                MessageBox.Show(ex.Message, "Create User Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnGetUser_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: Get User button clicked.");
                var id = ParseUserId();
                var user = _userApiClient.GetUser(id);
                BindUserResult(user);
                _logger.Info(string.Format("UI: User {0} loaded.", id));
            }
            catch (Exception ex)
            {
                _logger.Error("UI: Get user failed.", ex);
                MessageBox.Show(ex.Message, "Get User Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnUpdateUser_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: Update User button clicked.");
                var id = ParseUserId();
                var request = new UpdateUserRequestDto
                {
                    Username = txtUsername.Text.Trim(),
                    Email = txtEmail.Text.Trim(),
                    Phone = txtPhone.Text.Trim(),
                    FullName = txtFullName.Text.Trim()
                };

                var updated = _userApiClient.UpdateUser(id, request);
                BindUserResult(updated);
                _logger.Info(string.Format("UI: User {0} updated.", id));
            }
            catch (Exception ex)
            {
                _logger.Error("UI: Update user failed.", ex);
                MessageBox.Show(ex.Message, "Update User Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnDeleteUser_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: Delete User button clicked.");
                var id = ParseUserId();
                _userApiClient.DeleteUser(id);
                propertyGridUser.SelectedObject = null;
                _logger.Info(string.Format("UI: User {0} deleted.", id));
                MessageBox.Show("User deleted successfully.", "Delete User", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                _logger.Error("UI: Delete user failed.", ex);
                MessageBox.Show(ex.Message, "Delete User Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnCallAws_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: Call AWS API button clicked.");
                UseWaitCursor = true;
                btnCallAws.Enabled = false;

                var path = txtAwsPath.Text.Trim();
                var properties = _awsApiClient.FetchProperties(path);
                var rows = properties
                    .OrderBy(p => p.Key, StringComparer.OrdinalIgnoreCase)
                    .Select(p => new PropertyValueRow { Property = p.Key, Value = p.Value })
                    .ToList();

                dgvAwsProperties.DataSource = new BindingList<PropertyValueRow>(rows);
                lblAwsStatus.Text = string.Format("AWS response: {0} properties", rows.Count);
                lblAwsStatus.ForeColor = Color.DarkGreen;
                _logger.Info("UI: AWS properties bound to grid.");
            }
            catch (Exception ex)
            {
                lblAwsStatus.Text = "AWS call failed";
                lblAwsStatus.ForeColor = Color.DarkRed;
                _logger.Error("UI: AWS API call failed.", ex);
                MessageBox.Show(ex.Message, "AWS API Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                UseWaitCursor = false;
                btnCallAws.Enabled = true;
            }
        }

        private void BindUserResult(UserResponseDto user)
        {
            propertyGridUser.SelectedObject = user;
            propertyGridUser.Refresh();
        }

        private int ParseUserId()
        {
            int id;
            if (!int.TryParse(txtUserId.Text.Trim(), out id) || id <= 0)
            {
                if (_lastCreatedUserId > 0)
                {
                    id = _lastCreatedUserId;
                    txtUserId.Text = id.ToString();
                    return id;
                }

                throw new InvalidOperationException("Enter a valid user id.");
            }

            return id;
        }

        private void btnSnsPublish_Click(object sender, EventArgs e)
        {
            try
            {
                _logger.Info("UI: SNS Publish button clicked.");
                UseWaitCursor = true;
                btnSnsPublish.Enabled = false;

                // Local variables passed from UI to setup AWS profile credentials
                var profileName = txtSnsProfile.Text.Trim();
                var accessKey = txtSnsAccessKey.Text.Trim();
                var secretKey = txtSnsSecretKey.Text.Trim();
                var region = txtSnsRegion.Text.Trim();
                var topicArn = txtSnsTopicArn.Text.Trim();
                var message = txtSnsMessage.Text;

                var result = _awsSnsClient.PublishMessage(
                    profileName,
                    accessKey,
                    secretKey,
                    region,
                    topicArn,
                    message);

                BindSnsResult(result);
                lblSnsStatus.Text = string.Format("Published. MessageId={0}", result.MessageId);
                lblSnsStatus.ForeColor = Color.DarkGreen;
                _logger.Info(string.Format("UI: SNS publish completed. MessageId={0}.", result.MessageId));
            }
            catch (Exception ex)
            {
                lblSnsStatus.Text = "SNS publish failed";
                lblSnsStatus.ForeColor = Color.DarkRed;
                _logger.Error("UI: SNS publish failed.", ex);
                MessageBox.Show(ex.Message, "SNS Publish Failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                UseWaitCursor = false;
                btnSnsPublish.Enabled = true;
            }
        }
    }
}
