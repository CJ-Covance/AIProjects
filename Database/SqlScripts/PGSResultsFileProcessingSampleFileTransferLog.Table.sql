/*
    Logger: whether the four Embark Results Service files exist for an eligible sample.

    Sample identity and .ped composite identifier remain on the parent:
      dbo.PGSResultsFileProcessingDetails (ClientSampleID, CompositeID)

    Files associated with that sample (requirement):
      a. sampleID.report.tsv                         -> HasReportTsvFile
      b. sampleID.ped                                -> HasPedFile
      c. sentrixbarcode_sentrixposition_Red.idat     -> HasRedIdatFile
      d. sentrixbarcode_sentrixposition_Grn.idat     -> HasGrnIdatFile

    Path, file name, and file size are not stored. Existence is BIT: 1 = exists, 0 = does not exist.
    One log row per sample detail (1:1 via unique FK).
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_UpdateFileResult', N'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_UpdateFileResult;
GO

IF OBJECT_ID(N'dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeAttempt', N'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeAttempt;
GO

IF OBJECT_ID(N'dbo.vw_PGSResultsFileProcessingSampleFileTransferLog', N'V') IS NOT NULL
    DROP VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog;
GO

IF OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog', N'U') IS NOT NULL
    DROP TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog;
GO

CREATE TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog
(
    SampleFileTransferLogID INT          IDENTITY(1, 1) NOT NULL,
    FileProcessingDetailID  INT          NOT NULL,
    HasReportTsvFile        BIT          NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_HasReportTsvFile DEFAULT (0),
    HasPedFile              BIT          NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_HasPedFile DEFAULT (0),
    HasRedIdatFile          BIT          NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_HasRedIdatFile DEFAULT (0),
    HasGrnIdatFile          BIT          NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_HasGrnIdatFile DEFAULT (0),
    CreatedDate             DATETIME     NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_CreatedDate DEFAULT (GETDATE()),
    CreatedBy               NVARCHAR(22) NOT NULL,
    UpdatedDate             DATETIME     NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_UpdatedDate DEFAULT (GETDATE()),
    UpdatedBy               NVARCHAR(22) NOT NULL,

    CONSTRAINT PK_PGSResultsFileProcessingSampleFileTransferLog
        PRIMARY KEY CLUSTERED (SampleFileTransferLogID ASC),

    CONSTRAINT FK_PGSResultsFileTransferLog_PGSResultsFileProcessingDetails
        FOREIGN KEY (FileProcessingDetailID)
        REFERENCES dbo.PGSResultsFileProcessingDetails (FileProcessingDetailID),

    CONSTRAINT UQ_PGSResultsFileTransferLog_FileProcessingDetailID
        UNIQUE NONCLUSTERED (FileProcessingDetailID)
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
        l.HasReportTsvFile,
        l.HasPedFile,
        l.HasRedIdatFile,
        l.HasGrnIdatFile,
        CAST(
            CASE
                WHEN l.HasReportTsvFile = 1
                 AND l.HasPedFile = 1
                 AND l.HasRedIdatFile = 1
                 AND l.HasGrnIdatFile = 1
                THEN 1
                ELSE 0
            END AS BIT
        ) AS HasAllRequiredFiles,
        l.CreatedDate,
        l.CreatedBy,
        l.UpdatedDate,
        l.UpdatedBy
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
    INNER JOIN dbo.PGSResultsFileProcessingDetails AS d
        ON d.FileProcessingDetailID = l.FileProcessingDetailID
    INNER JOIN dbo.PGSResultsFileProcessing AS h
        ON h.FileProcessingID = d.FileProcessingID;
GO

CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExistence
(
    @FileProcessingDetailID INT,
    @HasReportTsvFile       BIT,
    @HasPedFile             BIT,
    @HasRedIdatFile         BIT,
    @HasGrnIdatFile         BIT,
    @UpdatedBy              NVARCHAR(22)
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

    IF NULLIF(LTRIM(RTRIM(@UpdatedBy)), N'') IS NULL
    BEGIN
        RAISERROR(N'@UpdatedBy is required.', 16, 1);
        RETURN;
    END;

    MERGE dbo.PGSResultsFileProcessingSampleFileTransferLog AS tgt
    USING (
        SELECT
            @FileProcessingDetailID AS FileProcessingDetailID,
            ISNULL(@HasReportTsvFile, 0) AS HasReportTsvFile,
            ISNULL(@HasPedFile, 0) AS HasPedFile,
            ISNULL(@HasRedIdatFile, 0) AS HasRedIdatFile,
            ISNULL(@HasGrnIdatFile, 0) AS HasGrnIdatFile
    ) AS src
        ON tgt.FileProcessingDetailID = src.FileProcessingDetailID
    WHEN MATCHED THEN
        UPDATE SET
            tgt.HasReportTsvFile = src.HasReportTsvFile,
            tgt.HasPedFile       = src.HasPedFile,
            tgt.HasRedIdatFile   = src.HasRedIdatFile,
            tgt.HasGrnIdatFile   = src.HasGrnIdatFile,
            tgt.UpdatedDate      = @Now,
            tgt.UpdatedBy        = @UpdatedBy
    WHEN NOT MATCHED THEN
        INSERT
        (
            FileProcessingDetailID,
            HasReportTsvFile,
            HasPedFile,
            HasRedIdatFile,
            HasGrnIdatFile,
            CreatedDate,
            CreatedBy,
            UpdatedDate,
            UpdatedBy
        )
        VALUES
        (
            src.FileProcessingDetailID,
            src.HasReportTsvFile,
            src.HasPedFile,
            src.HasRedIdatFile,
            src.HasGrnIdatFile,
            @Now,
            @UpdatedBy,
            @Now,
            @UpdatedBy
        );

    SELECT
        v.SampleFileTransferLogID,
        v.FileProcessingDetailID,
        v.ClientSampleID,
        v.CompositeID,
        v.HasReportTsvFile,
        v.HasPedFile,
        v.HasRedIdatFile,
        v.HasGrnIdatFile,
        v.HasAllRequiredFiles
    FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog AS v
    WHERE v.FileProcessingDetailID = @FileProcessingDetailID;
END;
GO

/*
EXEC dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_SetFileExistence
    @FileProcessingDetailID = 1,
    @HasReportTsvFile       = 1,
    @HasPedFile             = 1,
    @HasRedIdatFile         = 1,
    @HasGrnIdatFile         = 0,
    @UpdatedBy              = N'system';

SELECT *
FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog
WHERE FileProcessingDetailID = 1;
*/
