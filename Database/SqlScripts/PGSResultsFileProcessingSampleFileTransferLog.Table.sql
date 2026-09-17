/*
    Client-driven required-file catalog + sample file-existence log.

    Parent sample identity remains on dbo.PGSResultsFileProcessingDetails
    (ClientSampleID, CompositeID). File types are not hardcoded on the log table.

    For ClientID = NG0029 the catalog defines:
      a. sampleID.report.tsv                         REPORT_TSV
      b. sampleID.ped                                PED
      c. sentrixbarcode_sentrixposition_Red.idat     IDAT_RED
      d. sentrixbarcode_sentrixposition_Grn.idat     IDAT_GRN

    Additional clients get rows in PGSClientRequiredFileType without ALTER TABLE.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExistence', N'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExistence;
GO

IF OBJECT_ID(N'dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExists', N'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExists;
GO

IF OBJECT_ID(N'dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeForClient', N'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeForClient;
GO

IF OBJECT_ID(N'dbo.vw_PGSResultsFileProcessingSampleFileTransferLog_NG0029', N'V') IS NOT NULL
    DROP VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog_NG0029;
GO

IF OBJECT_ID(N'dbo.vw_PGSResultsFileProcessingSampleFileTransferLog', N'V') IS NOT NULL
    DROP VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog;
GO

IF OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog', N'U') IS NOT NULL
    DROP TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog;
GO

IF OBJECT_ID(N'dbo.PGSClientRequiredFileType', N'U') IS NOT NULL
    DROP TABLE dbo.PGSClientRequiredFileType;
GO

CREATE TABLE dbo.PGSClientRequiredFileType
(
    ClientRequiredFileTypeID INT           IDENTITY(1, 1) NOT NULL,
    ClientID                 NVARCHAR(20)  NOT NULL,
    FileTypeCode             NVARCHAR(20)  NOT NULL,
    FileDescription          NVARCHAR(150) NOT NULL,
    FileNamePattern          NVARCHAR(260) NOT NULL,
    DisplaySequence          INT           NOT NULL,
    IsActive                 BIT           NOT NULL
        CONSTRAINT DF_PGSClientRequiredFileType_IsActive DEFAULT (1),
    CreatedDate              DATETIME      NOT NULL
        CONSTRAINT DF_PGSClientRequiredFileType_CreatedDate DEFAULT (GETDATE()),
    CreatedBy                NVARCHAR(22)  NOT NULL,
    UpdatedDate              DATETIME      NOT NULL
        CONSTRAINT DF_PGSClientRequiredFileType_UpdatedDate DEFAULT (GETDATE()),
    UpdatedBy                NVARCHAR(22)  NOT NULL,

    CONSTRAINT PK_PGSClientRequiredFileType
        PRIMARY KEY CLUSTERED (ClientRequiredFileTypeID ASC),

    CONSTRAINT UQ_PGSClientRequiredFileType_Client_FileType
        UNIQUE NONCLUSTERED (ClientID, FileTypeCode),

    CONSTRAINT CK_PGSClientRequiredFileType_DisplaySequence
        CHECK (DisplaySequence >= 1)
);
GO

CREATE NONCLUSTERED INDEX IX_PGSClientRequiredFileType_ClientID_Active
    ON dbo.PGSClientRequiredFileType (ClientID, IsActive, DisplaySequence);
GO

CREATE TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog
(
    SampleFileTransferLogID    INT          IDENTITY(1, 1) NOT NULL,
    FileProcessingDetailID     INT          NOT NULL,
    ClientRequiredFileTypeID   INT          NOT NULL,
    FileExists                 BIT          NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_FileExists DEFAULT (0),
    CreatedDate                DATETIME     NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_CreatedDate DEFAULT (GETDATE()),
    CreatedBy                  NVARCHAR(22) NOT NULL,
    UpdatedDate                DATETIME     NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_UpdatedDate DEFAULT (GETDATE()),
    UpdatedBy                  NVARCHAR(22) NOT NULL,

    CONSTRAINT PK_PGSResultsFileProcessingSampleFileTransferLog
        PRIMARY KEY CLUSTERED (SampleFileTransferLogID ASC),

    CONSTRAINT FK_PGSResultsFileTransferLog_PGSResultsFileProcessingDetails
        FOREIGN KEY (FileProcessingDetailID)
        REFERENCES dbo.PGSResultsFileProcessingDetails (FileProcessingDetailID),

    CONSTRAINT FK_PGSResultsFileTransferLog_PGSClientRequiredFileType
        FOREIGN KEY (ClientRequiredFileTypeID)
        REFERENCES dbo.PGSClientRequiredFileType (ClientRequiredFileTypeID),

    CONSTRAINT UQ_PGSResultsFileTransferLog_Detail_FileType
        UNIQUE NONCLUSTERED (FileProcessingDetailID, ClientRequiredFileTypeID)
);
GO

CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_ClientRequiredFileTypeID
    ON dbo.PGSResultsFileProcessingSampleFileTransferLog (ClientRequiredFileTypeID)
    INCLUDE (FileExists, FileProcessingDetailID);
GO

/* NG0029 required files */
INSERT INTO dbo.PGSClientRequiredFileType
(
    ClientID,
    FileTypeCode,
    FileDescription,
    FileNamePattern,
    DisplaySequence,
    IsActive,
    CreatedDate,
    CreatedBy,
    UpdatedDate,
    UpdatedBy
)
VALUES
(
    N'NG0029',
    N'REPORT_TSV',
    N'sampleID.report.tsv',
    N'{ClientSampleID}.report.tsv',
    1,
    1,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
),
(
    N'NG0029',
    N'PED',
    N'sampleID.ped',
    N'{ClientSampleID}.ped',
    2,
    1,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
),
(
    N'NG0029',
    N'IDAT_RED',
    N'sentrixbarcode_sentrixposition_Red.idat',
    N'{SentrixBarcode}_{SentrixPosition}_Red.idat',
    3,
    1,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
),
(
    N'NG0029',
    N'IDAT_GRN',
    N'sentrixbarcode_sentrixposition_Grn.idat',
    N'{SentrixBarcode}_{SentrixPosition}_Grn.idat',
    4,
    1,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
),
(
    N'NG0029',
    N'JSONFile',
    N'sampleID.json',
    N'{ClientSampleID}.json',
    5,
    1,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
);
GO

CREATE OR ALTER VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog
AS
    SELECT
        l.SampleFileTransferLogID,
        l.FileProcessingDetailID,
        d.FileProcessingID,
        d.ClientSampleID,
        d.CompositeID,
        h.WGPlateID,
        ft.ClientID,
        ft.FileTypeCode,
        ft.FileDescription,
        ft.FileNamePattern,
        ft.DisplaySequence,
        l.FileExists,
        l.CreatedDate,
        l.CreatedBy,
        l.UpdatedDate,
        l.UpdatedBy
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
    INNER JOIN dbo.PGSClientRequiredFileType AS ft
        ON ft.ClientRequiredFileTypeID = l.ClientRequiredFileTypeID
    INNER JOIN dbo.PGSResultsFileProcessingDetails AS d
        ON d.FileProcessingDetailID = l.FileProcessingDetailID
    INNER JOIN dbo.PGSResultsFileProcessing AS h
        ON h.FileProcessingID = d.FileProcessingID;
GO

/* Same four flags as the previous log table, driven by NG0029 catalog rows. */
CREATE OR ALTER VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog_NG0029
AS
    SELECT
        d.FileProcessingDetailID,
        d.FileProcessingID,
        d.ClientSampleID,
        d.CompositeID,
        h.WGPlateID,
        CAST(MAX(CASE WHEN ft.FileTypeCode = N'REPORT_TSV' THEN CAST(l.FileExists AS INT) ELSE 0 END) AS BIT) AS HasReportTsvFile,
        CAST(MAX(CASE WHEN ft.FileTypeCode = N'PED' THEN CAST(l.FileExists AS INT) ELSE 0 END) AS BIT) AS HasPedFile,
        CAST(MAX(CASE WHEN ft.FileTypeCode = N'IDAT_RED' THEN CAST(l.FileExists AS INT) ELSE 0 END) AS BIT) AS HasRedIdatFile,
        CAST(MAX(CASE WHEN ft.FileTypeCode = N'IDAT_GRN' THEN CAST(l.FileExists AS INT) ELSE 0 END) AS BIT) AS HasGrnIdatFile,
        CAST(
            CASE
                WHEN MIN(CAST(l.FileExists AS INT)) = 1
                 AND COUNT(*) = 5
                THEN 1
                ELSE 0
            END AS BIT
        ) AS HasAllRequiredFiles
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
    INNER JOIN dbo.PGSClientRequiredFileType AS ft
        ON ft.ClientRequiredFileTypeID = l.ClientRequiredFileTypeID
    INNER JOIN dbo.PGSResultsFileProcessingDetails AS d
        ON d.FileProcessingDetailID = l.FileProcessingDetailID
    INNER JOIN dbo.PGSResultsFileProcessing AS h
        ON h.FileProcessingID = d.FileProcessingID
    WHERE ft.ClientID = N'NG0029'
      AND ft.IsActive = 1
    GROUP BY
        d.FileProcessingDetailID,
        d.FileProcessingID,
        d.ClientSampleID,
        d.CompositeID,
        h.WGPlateID;
GO

CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeForClient
(
    @FileProcessingDetailID INT,
    @ClientID               NVARCHAR(20),
    @CreatedBy              NVARCHAR(22)
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingDetails AS d
        WHERE d.FileProcessingDetailID = @FileProcessingDetailID
    )
    BEGIN
        RAISERROR(N'FileProcessingDetailID %d not found.', 16, 1, @FileProcessingDetailID);
        RETURN;
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.PGSClientRequiredFileType AS ft
        WHERE ft.ClientID = @ClientID
          AND ft.IsActive = 1
    )
    BEGIN
        RAISERROR(N'No active required file types are defined for ClientID %s.', 16, 1, @ClientID);
        RETURN;
    END;

    IF NULLIF(LTRIM(RTRIM(@CreatedBy)), N'') IS NULL
    BEGIN
        RAISERROR(N'@CreatedBy is required.', 16, 1);
        RETURN;
    END;

    INSERT INTO dbo.PGSResultsFileProcessingSampleFileTransferLog
    (
        FileProcessingDetailID,
        ClientRequiredFileTypeID,
        FileExists,
        CreatedDate,
        CreatedBy,
        UpdatedDate,
        UpdatedBy
    )
    SELECT
        @FileProcessingDetailID,
        ft.ClientRequiredFileTypeID,
        0,
        @Now,
        @CreatedBy,
        @Now,
        @CreatedBy
    FROM dbo.PGSClientRequiredFileType AS ft
    WHERE ft.ClientID = @ClientID
      AND ft.IsActive = 1
      AND NOT EXISTS (
            SELECT 1
            FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
            WHERE l.FileProcessingDetailID = @FileProcessingDetailID
              AND l.ClientRequiredFileTypeID = ft.ClientRequiredFileTypeID
          );

    SELECT
        v.SampleFileTransferLogID,
        v.FileProcessingDetailID,
        v.ClientSampleID,
        v.ClientID,
        v.FileTypeCode,
        v.FileDescription,
        v.FileExists
    FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog AS v
    WHERE v.FileProcessingDetailID = @FileProcessingDetailID
      AND v.ClientID = @ClientID
    ORDER BY v.DisplaySequence;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExists
(
    @FileProcessingDetailID INT,
    @ClientID               NVARCHAR(20),
    @FileTypeCode           NVARCHAR(20),
    @FileExists             BIT,
    @UpdatedBy              NVARCHAR(22)
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();
    DECLARE @ClientRequiredFileTypeID INT;

    SELECT @ClientRequiredFileTypeID = ft.ClientRequiredFileTypeID
    FROM dbo.PGSClientRequiredFileType AS ft
    WHERE ft.ClientID = @ClientID
      AND ft.FileTypeCode = @FileTypeCode
      AND ft.IsActive = 1;

    IF @ClientRequiredFileTypeID IS NULL
    BEGIN
        RAISERROR(N'File type %s is not defined for ClientID %s.', 16, 1, @FileTypeCode, @ClientID);
        RETURN;
    END;

    UPDATE l
    SET
        l.FileExists  = ISNULL(@FileExists, 0),
        l.UpdatedDate = @Now,
        l.UpdatedBy   = @UpdatedBy
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
    WHERE l.FileProcessingDetailID = @FileProcessingDetailID
      AND l.ClientRequiredFileTypeID = @ClientRequiredFileTypeID;

    IF @@ROWCOUNT = 0
    BEGIN
        RAISERROR(N'No log row for FileProcessingDetailID %d and file type %s. Run InitializeForClient first.', 16, 1, @FileProcessingDetailID, @FileTypeCode);
        RETURN;
    END;
END;
GO
