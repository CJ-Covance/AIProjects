/*
    Final report file detail per sample (one row per required file).

    Shared with PGSResultsFileProcessingDetails:
      FileProcessingDetailID (FK), ClientSampleID

    File kinds (stored in FileType, not as separate BIT columns):
      ReportTsvFile, PedFile, RedIdatFile, GrnIdatFile, JSONFile

    IsFileExist is stored. IsFileMissing is computed as NOT IsFileExist.
    CreatedOn / UpdatedOn hold the user (same role as CreatedBy / UpdatedBy on parent tables).
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.PGSResultsFileProcessingFinalReportFileDetail', N'U') IS NOT NULL
    DROP TABLE dbo.PGSResultsFileProcessingFinalReportFileDetail;
GO

CREATE TABLE dbo.PGSResultsFileProcessingFinalReportFileDetail
(
    FinalReportFileDetailID INT           IDENTITY(1, 1) NOT NULL,
    FileProcessingDetailID  INT           NOT NULL,
    ClientSampleID          NVARCHAR(36)  NOT NULL,
    FileType                NVARCHAR(20)  NOT NULL,
    FileName                NVARCHAR(260) NOT NULL,
    IsFileExist             BIT           NOT NULL
        CONSTRAINT DF_FinalReportFileDetail_IsFileExist DEFAULT (0),
    IsFileMissing           AS (
                                CAST(CASE WHEN IsFileExist = 1 THEN 0 ELSE 1 END AS BIT)
                               ) PERSISTED,
    IsFileTransfered        BIT           NOT NULL
        CONSTRAINT DF_FinalReportFileDetail_IsFileTransfered DEFAULT (0),
    CreatedDate             DATETIME      NOT NULL
        CONSTRAINT DF_FinalReportFileDetail_CreatedDate DEFAULT (GETDATE()),
    CreatedOn               NVARCHAR(22)  NOT NULL,
    UpdatedDate             DATETIME      NOT NULL
        CONSTRAINT DF_FinalReportFileDetail_UpdatedDate DEFAULT (GETDATE()),
    UpdatedOn               NVARCHAR(22)  NOT NULL,
    TransferDate            DATETIME      NULL,

    CONSTRAINT PK_PGSResultsFileProcessingFinalReportFileDetail
        PRIMARY KEY CLUSTERED (FinalReportFileDetailID ASC),

    CONSTRAINT FK_FinalReportFileDetail_PGSResultsFileProcessingDetails
        FOREIGN KEY (FileProcessingDetailID)
        REFERENCES dbo.PGSResultsFileProcessingDetails (FileProcessingDetailID),

    CONSTRAINT CK_FinalReportFileDetail_FileType
        CHECK (FileType IN (
            N'ReportTsvFile',
            N'PedFile',
            N'RedIdatFile',
            N'GrnIdatFile',
            N'JSONFile'
        )),

    CONSTRAINT UQ_FinalReportFileDetail_Detail_FileType
        UNIQUE NONCLUSTERED (FileProcessingDetailID, FileType)
);
GO

CREATE NONCLUSTERED INDEX IX_FinalReportFileDetail_ClientSampleID
    ON dbo.PGSResultsFileProcessingFinalReportFileDetail (ClientSampleID)
    INCLUDE (FileType, FileName, IsFileExist, IsFileTransfered);
GO

CREATE NONCLUSTERED INDEX IX_FinalReportFileDetail_FileProcessingDetailID
    ON dbo.PGSResultsFileProcessingFinalReportFileDetail (FileProcessingDetailID)
    INCLUDE (FileType, FileName, IsFileExist, IsFileTransfered, TransferDate);
GO

IF OBJECT_ID(N'dbo.PGSClientRequiredFileType', N'U') IS NOT NULL
BEGIN
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
    SELECT
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
    WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.PGSClientRequiredFileType AS ft
        WHERE ft.ClientID = N'NG0029'
          AND ft.FileTypeCode = N'JSONFile'
    );
END;
GO
