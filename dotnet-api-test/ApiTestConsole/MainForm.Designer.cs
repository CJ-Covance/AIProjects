namespace ApiTestConsole
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.SplitContainer splitMain;
        private System.Windows.Forms.TabControl tabActions;
        private System.Windows.Forms.TabPage tabUserApi;
        private System.Windows.Forms.TabPage tabAwsApi;
        private System.Windows.Forms.GroupBox grpUserInput;
        private System.Windows.Forms.Label lblUsername;
        private System.Windows.Forms.TextBox txtUsername;
        private System.Windows.Forms.Label lblEmail;
        private System.Windows.Forms.TextBox txtEmail;
        private System.Windows.Forms.Label lblPhone;
        private System.Windows.Forms.TextBox txtPhone;
        private System.Windows.Forms.Label lblFullName;
        private System.Windows.Forms.TextBox txtFullName;
        private System.Windows.Forms.Label lblUserId;
        private System.Windows.Forms.TextBox txtUserId;
        private System.Windows.Forms.Button btnCreateUser;
        private System.Windows.Forms.Button btnGetUser;
        private System.Windows.Forms.Button btnUpdateUser;
        private System.Windows.Forms.Button btnDeleteUser;
        private System.Windows.Forms.Label lblAwsPath;
        private System.Windows.Forms.TextBox txtAwsPath;
        private System.Windows.Forms.Button btnCallAws;
        private System.Windows.Forms.Label lblAwsStatus;
        private System.Windows.Forms.SplitContainer splitRight;
        private System.Windows.Forms.PropertyGrid propertyGridUser;
        private System.Windows.Forms.DataGridView dgvAwsProperties;
        private System.Windows.Forms.GroupBox grpLog;
        private System.Windows.Forms.TextBox txtLog;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }

            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.splitMain = new System.Windows.Forms.SplitContainer();
            this.tabActions = new System.Windows.Forms.TabControl();
            this.tabUserApi = new System.Windows.Forms.TabPage();
            this.btnDeleteUser = new System.Windows.Forms.Button();
            this.btnUpdateUser = new System.Windows.Forms.Button();
            this.btnGetUser = new System.Windows.Forms.Button();
            this.btnCreateUser = new System.Windows.Forms.Button();
            this.grpUserInput = new System.Windows.Forms.GroupBox();
            this.txtUserId = new System.Windows.Forms.TextBox();
            this.lblUserId = new System.Windows.Forms.Label();
            this.txtFullName = new System.Windows.Forms.TextBox();
            this.lblFullName = new System.Windows.Forms.Label();
            this.txtPhone = new System.Windows.Forms.TextBox();
            this.lblPhone = new System.Windows.Forms.Label();
            this.txtEmail = new System.Windows.Forms.TextBox();
            this.lblEmail = new System.Windows.Forms.Label();
            this.txtUsername = new System.Windows.Forms.TextBox();
            this.lblUsername = new System.Windows.Forms.Label();
            this.tabAwsApi = new System.Windows.Forms.TabPage();
            this.lblAwsStatus = new System.Windows.Forms.Label();
            this.btnCallAws = new System.Windows.Forms.Button();
            this.txtAwsPath = new System.Windows.Forms.TextBox();
            this.lblAwsPath = new System.Windows.Forms.Label();
            this.splitRight = new System.Windows.Forms.SplitContainer();
            this.propertyGridUser = new System.Windows.Forms.PropertyGrid();
            this.dgvAwsProperties = new System.Windows.Forms.DataGridView();
            this.grpLog = new System.Windows.Forms.GroupBox();
            this.txtLog = new System.Windows.Forms.TextBox();
            ((System.ComponentModel.ISupportInitialize)(this.splitMain)).BeginInit();
            this.splitMain.Panel1.SuspendLayout();
            this.splitMain.Panel2.SuspendLayout();
            this.splitMain.SuspendLayout();
            this.tabActions.SuspendLayout();
            this.tabUserApi.SuspendLayout();
            this.grpUserInput.SuspendLayout();
            this.tabAwsApi.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitRight)).BeginInit();
            this.splitRight.Panel1.SuspendLayout();
            this.splitRight.Panel2.SuspendLayout();
            this.splitRight.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvAwsProperties)).BeginInit();
            this.grpLog.SuspendLayout();
            this.SuspendLayout();
            // 
            // splitMain
            // 
            this.splitMain.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitMain.Location = new System.Drawing.Point(0, 0);
            this.splitMain.Name = "splitMain";
            this.splitMain.Orientation = System.Windows.Forms.Orientation.Vertical;
            // 
            // splitMain.Panel1
            // 
            this.splitMain.Panel1.Controls.Add(this.tabActions);
            // 
            // splitMain.Panel2
            // 
            this.splitMain.Panel2.Controls.Add(this.splitRight);
            this.splitMain.Panel2.Controls.Add(this.grpLog);
            this.splitMain.Size = new System.Drawing.Size(1184, 761);
            this.splitMain.SplitterDistance = 380;
            this.splitMain.TabIndex = 0;
            // 
            // tabActions
            // 
            this.tabActions.Controls.Add(this.tabUserApi);
            this.tabActions.Controls.Add(this.tabAwsApi);
            this.tabActions.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabActions.Location = new System.Drawing.Point(0, 0);
            this.tabActions.Name = "tabActions";
            this.tabActions.SelectedIndex = 0;
            this.tabActions.Size = new System.Drawing.Size(380, 761);
            this.tabActions.TabIndex = 0;
            // 
            // tabUserApi
            // 
            this.tabUserApi.Controls.Add(this.btnDeleteUser);
            this.tabUserApi.Controls.Add(this.btnUpdateUser);
            this.tabUserApi.Controls.Add(this.btnGetUser);
            this.tabUserApi.Controls.Add(this.btnCreateUser);
            this.tabUserApi.Controls.Add(this.grpUserInput);
            this.tabUserApi.Location = new System.Drawing.Point(4, 29);
            this.tabUserApi.Name = "tabUserApi";
            this.tabUserApi.Padding = new System.Windows.Forms.Padding(3);
            this.tabUserApi.Size = new System.Drawing.Size(372, 728);
            this.tabUserApi.TabIndex = 0;
            this.tabUserApi.Text = "User API";
            this.tabUserApi.UseVisualStyleBackColor = true;
            // 
            // btnDeleteUser
            // 
            this.btnDeleteUser.Location = new System.Drawing.Point(194, 390);
            this.btnDeleteUser.Name = "btnDeleteUser";
            this.btnDeleteUser.Size = new System.Drawing.Size(160, 40);
            this.btnDeleteUser.TabIndex = 4;
            this.btnDeleteUser.Text = "DELETE User";
            this.btnDeleteUser.UseVisualStyleBackColor = true;
            this.btnDeleteUser.Click += new System.EventHandler(this.btnDeleteUser_Click);
            // 
            // btnUpdateUser
            // 
            this.btnUpdateUser.Location = new System.Drawing.Point(16, 390);
            this.btnUpdateUser.Name = "btnUpdateUser";
            this.btnUpdateUser.Size = new System.Drawing.Size(160, 40);
            this.btnUpdateUser.TabIndex = 3;
            this.btnUpdateUser.Text = "PUT Update User";
            this.btnUpdateUser.UseVisualStyleBackColor = true;
            this.btnUpdateUser.Click += new System.EventHandler(this.btnUpdateUser_Click);
            // 
            // btnGetUser
            // 
            this.btnGetUser.Location = new System.Drawing.Point(194, 334);
            this.btnGetUser.Name = "btnGetUser";
            this.btnGetUser.Size = new System.Drawing.Size(160, 40);
            this.btnGetUser.TabIndex = 2;
            this.btnGetUser.Text = "GET User";
            this.btnGetUser.UseVisualStyleBackColor = true;
            this.btnGetUser.Click += new System.EventHandler(this.btnGetUser_Click);
            // 
            // btnCreateUser
            // 
            this.btnCreateUser.Location = new System.Drawing.Point(16, 334);
            this.btnCreateUser.Name = "btnCreateUser";
            this.btnCreateUser.Size = new System.Drawing.Size(160, 40);
            this.btnCreateUser.TabIndex = 1;
            this.btnCreateUser.Text = "POST Create User";
            this.btnCreateUser.UseVisualStyleBackColor = true;
            this.btnCreateUser.Click += new System.EventHandler(this.btnCreateUser_Click);
            // 
            // grpUserInput
            // 
            this.grpUserInput.Controls.Add(this.txtUserId);
            this.grpUserInput.Controls.Add(this.lblUserId);
            this.grpUserInput.Controls.Add(this.txtFullName);
            this.grpUserInput.Controls.Add(this.lblFullName);
            this.grpUserInput.Controls.Add(this.txtPhone);
            this.grpUserInput.Controls.Add(this.lblPhone);
            this.grpUserInput.Controls.Add(this.txtEmail);
            this.grpUserInput.Controls.Add(this.lblEmail);
            this.grpUserInput.Controls.Add(this.txtUsername);
            this.grpUserInput.Controls.Add(this.lblUsername);
            this.grpUserInput.Dock = System.Windows.Forms.DockStyle.Top;
            this.grpUserInput.Location = new System.Drawing.Point(3, 3);
            this.grpUserInput.Name = "grpUserInput";
            this.grpUserInput.Size = new System.Drawing.Size(366, 310);
            this.grpUserInput.TabIndex = 0;
            this.grpUserInput.TabStop = false;
            this.grpUserInput.Text = "User Payload";
            // 
            // txtUserId
            // 
            this.txtUserId.Location = new System.Drawing.Point(120, 250);
            this.txtUserId.Name = "txtUserId";
            this.txtUserId.Size = new System.Drawing.Size(220, 29);
            this.txtUserId.TabIndex = 9;
            // 
            // lblUserId
            // 
            this.lblUserId.AutoSize = true;
            this.lblUserId.Location = new System.Drawing.Point(16, 253);
            this.lblUserId.Name = "lblUserId";
            this.lblUserId.Size = new System.Drawing.Size(62, 24);
            this.lblUserId.TabIndex = 8;
            this.lblUserId.Text = "User Id";
            // 
            // txtFullName
            // 
            this.txtFullName.Location = new System.Drawing.Point(120, 196);
            this.txtFullName.Name = "txtFullName";
            this.txtFullName.Size = new System.Drawing.Size(220, 29);
            this.txtFullName.TabIndex = 7;
            this.txtFullName.Text = "Jane Doe";
            // 
            // lblFullName
            // 
            this.lblFullName.AutoSize = true;
            this.lblFullName.Location = new System.Drawing.Point(16, 199);
            this.lblFullName.Name = "lblFullName";
            this.lblFullName.Size = new System.Drawing.Size(86, 24);
            this.lblFullName.TabIndex = 6;
            this.lblFullName.Text = "Full Name";
            // 
            // txtPhone
            // 
            this.txtPhone.Location = new System.Drawing.Point(120, 142);
            this.txtPhone.Name = "txtPhone";
            this.txtPhone.Size = new System.Drawing.Size(220, 29);
            this.txtPhone.TabIndex = 5;
            this.txtPhone.Text = "+1-555-0100";
            // 
            // lblPhone
            // 
            this.lblPhone.AutoSize = true;
            this.lblPhone.Location = new System.Drawing.Point(16, 145);
            this.lblPhone.Name = "lblPhone";
            this.lblPhone.Size = new System.Drawing.Size(62, 24);
            this.lblPhone.TabIndex = 4;
            this.lblPhone.Text = "Phone";
            // 
            // txtEmail
            // 
            this.txtEmail.Location = new System.Drawing.Point(120, 88);
            this.txtEmail.Name = "txtEmail";
            this.txtEmail.Size = new System.Drawing.Size(220, 29);
            this.txtEmail.TabIndex = 3;
            this.txtEmail.Text = "jane.doe@example.com";
            // 
            // lblEmail
            // 
            this.lblEmail.AutoSize = true;
            this.lblEmail.Location = new System.Drawing.Point(16, 91);
            this.lblEmail.Name = "lblEmail";
            this.lblEmail.Size = new System.Drawing.Size(53, 24);
            this.lblEmail.TabIndex = 2;
            this.lblEmail.Text = "Email";
            // 
            // txtUsername
            // 
            this.txtUsername.Location = new System.Drawing.Point(120, 34);
            this.txtUsername.Name = "txtUsername";
            this.txtUsername.Size = new System.Drawing.Size(220, 29);
            this.txtUsername.TabIndex = 1;
            this.txtUsername.Text = "jane_doe";
            // 
            // lblUsername
            // 
            this.lblUsername.AutoSize = true;
            this.lblUsername.Location = new System.Drawing.Point(16, 37);
            this.lblUsername.Name = "lblUsername";
            this.lblUsername.Size = new System.Drawing.Size(90, 24);
            this.lblUsername.TabIndex = 0;
            this.lblUsername.Text = "Username";
            // 
            // tabAwsApi
            // 
            this.tabAwsApi.Controls.Add(this.lblAwsStatus);
            this.tabAwsApi.Controls.Add(this.btnCallAws);
            this.tabAwsApi.Controls.Add(this.txtAwsPath);
            this.tabAwsApi.Controls.Add(this.lblAwsPath);
            this.tabAwsApi.Location = new System.Drawing.Point(4, 29);
            this.tabAwsApi.Name = "tabAwsApi";
            this.tabAwsApi.Padding = new System.Windows.Forms.Padding(3);
            this.tabAwsApi.Size = new System.Drawing.Size(372, 728);
            this.tabAwsApi.TabIndex = 1;
            this.tabAwsApi.Text = "AWS API (IMP)";
            this.tabAwsApi.UseVisualStyleBackColor = true;
            // 
            // lblAwsStatus
            // 
            this.lblAwsStatus.AutoSize = true;
            this.lblAwsStatus.Location = new System.Drawing.Point(16, 140);
            this.lblAwsStatus.Name = "lblAwsStatus";
            this.lblAwsStatus.Size = new System.Drawing.Size(233, 24);
            this.lblAwsStatus.TabIndex = 3;
            this.lblAwsStatus.Text = "Ready to call AWS API";
            // 
            // btnCallAws
            // 
            this.btnCallAws.Location = new System.Drawing.Point(16, 84);
            this.btnCallAws.Name = "btnCallAws";
            this.btnCallAws.Size = new System.Drawing.Size(338, 40);
            this.btnCallAws.TabIndex = 2;
            this.btnCallAws.Text = "Call AWS API && Show Properties";
            this.btnCallAws.UseVisualStyleBackColor = true;
            this.btnCallAws.Click += new System.EventHandler(this.btnCallAws_Click);
            // 
            // txtAwsPath
            // 
            this.txtAwsPath.Location = new System.Drawing.Point(16, 44);
            this.txtAwsPath.Name = "txtAwsPath";
            this.txtAwsPath.Size = new System.Drawing.Size(338, 29);
            this.txtAwsPath.TabIndex = 1;
            // 
            // lblAwsPath
            // 
            this.lblAwsPath.AutoSize = true;
            this.lblAwsPath.Location = new System.Drawing.Point(16, 16);
            this.lblAwsPath.Name = "lblAwsPath";
            this.lblAwsPath.Size = new System.Drawing.Size(247, 24);
            this.lblAwsPath.TabIndex = 0;
            this.lblAwsPath.Text = "AWS Resource Path (optional)";
            // 
            // splitRight
            // 
            this.splitRight.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitRight.Location = new System.Drawing.Point(0, 0);
            this.splitRight.Name = "splitRight";
            this.splitRight.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitRight.Panel1
            // 
            this.splitRight.Panel1.Controls.Add(this.propertyGridUser);
            // 
            // splitRight.Panel2
            // 
            this.splitRight.Panel2.Controls.Add(this.dgvAwsProperties);
            this.splitRight.Size = new System.Drawing.Size(800, 561);
            this.splitRight.SplitterDistance = 260;
            this.splitRight.TabIndex = 0;
            // 
            // propertyGridUser
            // 
            this.propertyGridUser.CommandsVisibleIfAvailable = false;
            this.propertyGridUser.Dock = System.Windows.Forms.DockStyle.Fill;
            this.propertyGridUser.HelpVisible = false;
            this.propertyGridUser.Location = new System.Drawing.Point(0, 0);
            this.propertyGridUser.Name = "propertyGridUser";
            this.propertyGridUser.PropertySort = System.Windows.Forms.PropertySort.Alphabetical;
            this.propertyGridUser.Size = new System.Drawing.Size(800, 260);
            this.propertyGridUser.TabIndex = 0;
            this.propertyGridUser.ToolbarVisible = false;
            // 
            // dgvAwsProperties
            // 
            this.dgvAwsProperties.AllowUserToAddRows = false;
            this.dgvAwsProperties.AllowUserToDeleteRows = false;
            this.dgvAwsProperties.BackgroundColor = System.Drawing.SystemColors.Window;
            this.dgvAwsProperties.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvAwsProperties.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dgvAwsProperties.Location = new System.Drawing.Point(0, 0);
            this.dgvAwsProperties.Name = "dgvAwsProperties";
            this.dgvAwsProperties.ReadOnly = true;
            this.dgvAwsProperties.RowHeadersVisible = false;
            this.dgvAwsProperties.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvAwsProperties.Size = new System.Drawing.Size(800, 297);
            this.dgvAwsProperties.TabIndex = 0;
            // 
            // grpLog
            // 
            this.grpLog.Controls.Add(this.txtLog);
            this.grpLog.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.grpLog.Location = new System.Drawing.Point(0, 561);
            this.grpLog.Name = "grpLog";
            this.grpLog.Size = new System.Drawing.Size(800, 200);
            this.grpLog.TabIndex = 1;
            this.grpLog.TabStop = false;
            this.grpLog.Text = "Step Logger";
            // 
            // txtLog
            // 
            this.txtLog.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(24)))), ((int)(((byte)(24)))), ((int)(((byte)(24)))));
            this.txtLog.Dock = System.Windows.Forms.DockStyle.Fill;
            this.txtLog.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(220)))), ((int)(((byte)(220)))), ((int)(((byte)(220)))));
            this.txtLog.Location = new System.Drawing.Point(3, 25);
            this.txtLog.Multiline = true;
            this.txtLog.Name = "txtLog";
            this.txtLog.ReadOnly = true;
            this.txtLog.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtLog.Size = new System.Drawing.Size(794, 172);
            this.txtLog.TabIndex = 0;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(10F, 24F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1184, 761);
            this.Controls.Add(this.splitMain);
            this.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.MinimumSize = new System.Drawing.Size(1000, 700);
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "API Test Console — User API + AWS (IMP)";
            this.splitMain.Panel1.ResumeLayout(false);
            this.splitMain.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitMain)).EndInit();
            this.splitMain.ResumeLayout(false);
            this.tabActions.ResumeLayout(false);
            this.tabUserApi.ResumeLayout(false);
            this.grpUserInput.ResumeLayout(false);
            this.grpUserInput.PerformLayout();
            this.tabAwsApi.ResumeLayout(false);
            this.tabAwsApi.PerformLayout();
            this.splitRight.Panel1.ResumeLayout(false);
            this.splitRight.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitRight)).EndInit();
            this.splitRight.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvAwsProperties)).EndInit();
            this.grpLog.ResumeLayout(false);
            this.grpLog.PerformLayout();
            this.ResumeLayout(false);
        }
    }
}
