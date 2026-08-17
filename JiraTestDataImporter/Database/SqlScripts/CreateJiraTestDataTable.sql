-- Creates the JiraTestData table used by JiraTestDataImporter.
-- Run this script against the target SQL Server database before importing data.

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE name = 'JiraTestData'
      AND schema_id = SCHEMA_ID('dbo')
)
BEGIN
    CREATE TABLE dbo.JiraTestData
    (
        TestDataId INT IDENTITY(1,1) NOT NULL PRIMARY KEY,

        JiraIssueId VARCHAR(100) NOT NULL,
        JiraIssueKey VARCHAR(100) NOT NULL,

        ProjectKey VARCHAR(50) NULL,

        Summary NVARCHAR(500) NULL,

        Description NVARCHAR(MAX) NULL,

        Status VARCHAR(100) NULL,

        Priority VARCHAR(100) NULL,

        Assignee VARCHAR(255) NULL,

        CreatedDate DATETIME NULL,

        UpdatedDate DATETIME NULL,

        ImportedDate DATETIME NOT NULL CONSTRAINT DF_JiraTestData_ImportedDate DEFAULT (GETDATE())
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_JiraTestData_JiraIssueKey'
      AND object_id = OBJECT_ID('dbo.JiraTestData')
)
BEGIN
    CREATE UNIQUE INDEX UX_JiraTestData_JiraIssueKey
        ON dbo.JiraTestData (JiraIssueKey);
END
GO
