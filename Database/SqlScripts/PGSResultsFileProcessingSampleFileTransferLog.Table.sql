/*
    Logger: Embark Results Service file transfer per eligible sample.

    Parent identity (ClientSampleID, CompositeID, eligibility, plate) lives only on
    dbo.PGSResultsFileProcessingDetails. This table stores one row per file transferred
    per attempt, keyed by FileProcessingDetailID (FK).

    Files per eligible sample (CompositeID = .ped composite on parent detail row):
      a. {ClientSampleID}.report.tsv
      b. {ClientSampleID}.ped
      c. {SentrixBarcode}_{SentrixPosition}_Red.idat
      d. {SentrixBarcode}_{SentrixPosition}_Grn.idat
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* Recreate: drop child logger if present (no other tables reference this table). */
IF OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog;
END;
GO

CREATE TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog
(
    SampleFileTransferLogID INT           IDENTITY(1, 1) NOT NULL,
    FileProcessingDetailID  INT           NOT NULL,
    TransferAttemptNumber   INT           NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_TransferAttemptNumber DEFAULT (1),
    FileType                NVARCHAR(20)  NOT NULL,
    ExpectedFileName        NVARCHAR(260) NOT NULL,
    SourceFilePath          NVARCHAR(500) NULL,
    DestinationFilePath     NVARCHAR(500) NULL,
    TransferStatus          NVARCHAR(20)  NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_TransferStatus DEFAULT (N'Pending'),
    ErrorMessage            NVARCHAR(500) NULL,
    FileSizeBytes           BIGINT        NULL,
    TransferStartedDate     DATETIME      NULL,
    TransferCompletedDate   DATETIME      NULL,
    CreatedDate             DATETIME      NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_CreatedDate DEFAULT (GETDATE()),
    CreatedBy               NVARCHAR(22)  NOT NULL,
    UpdatedDate             DATETIME      NOT NULL
        CONSTRAINT DF_PGSResultsFileTransferLog_UpdatedDate DEFAULT (GETDATE()),
    UpdatedBy               NVARCHAR(22)  NOT NULL,

    CONSTRAINT PK_PGSResultsFileProcessingSampleFileTransferLog
        PRIMARY KEY CLUSTERED (SampleFileTransferLogID ASC),

    CONSTRAINT FK_PGSResultsFileTransferLog_PGSResultsFileProcessingDetails
        FOREIGN KEY (FileProcessingDetailID)
        REFERENCES dbo.PGSResultsFileProcessingDetails (FileProcessingDetailID),

    CONSTRAINT CK_PGSResultsFileTransferLog_FileType
        CHECK (FileType IN (N'REPORT_TSV', N'PED', N'IDAT_RED', N'IDAT_GRN')),

    CONSTRAINT CK_PGSResultsFileTransferLog_TransferStatus
        CHECK (TransferStatus IN (N'Pending', N'InProgress', N'Success', N'Failed', N'Skipped')),

    CONSTRAINT CK_PGSResultsFileTransferLog_TransferAttemptNumber
        CHECK (TransferAttemptNumber >= 1),

    CONSTRAINT UQ_PGSResultsFileTransferLog_Detail_Attempt_FileType
        UNIQUE NONCLUSTERED (
            FileProcessingDetailID,
            TransferAttemptNumber,
            FileType
        )
);
GO

CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_FileProcessingDetailID
    ON dbo.PGSResultsFileProcessingSampleFileTransferLog (FileProcessingDetailID, TransferAttemptNumber)
    INCLUDE (FileType, TransferStatus, ExpectedFileName, TransferCompletedDate);
GO

CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_Status_Pending
    ON dbo.PGSResultsFileProcessingSampleFileTransferLog (TransferStatus, FileProcessingDetailID)
    WHERE TransferStatus IN (N'Pending', N'InProgress');
GO

/* Reporting: sample / composite from parent via FK — not duplicated on log rows. */
CREATE OR ALTER VIEW dbo.vw_PGSResultsFileProcessingSampleFileTransferLog
AS
    SELECT
        l.SampleFileTransferLogID,
        l.FileProcessingDetailID,
        d.FileProcessingID,
        d.ClientSampleID,
        d.CompositeID,
        h.WGPlateID,
        l.TransferAttemptNumber,
        l.FileType,
        l.ExpectedFileName,
        l.SourceFilePath,
        l.DestinationFilePath,
        l.TransferStatus,
        l.ErrorMessage,
        l.FileSizeBytes,
        l.TransferStartedDate,
        l.TransferCompletedDate,
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

/* ============================================================================
   Initialize four file log rows for one eligible sample transfer attempt.
   ============================================================================ */
CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeAttempt
(
    @FileProcessingDetailID INT,
    @DestinationRootPath    NVARCHAR(500),
    @SentrixBarcode         NVARCHAR(50),
    @SentrixPosition        NVARCHAR(50),
    @TransferAttemptNumber  INT           = NULL,
    @CreatedBy              NVARCHAR(22),
    @SourceDirectoryPath    NVARCHAR(500) = NULL
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();
    DECLARE @ClientSampleID NVARCHAR(36);
    DECLARE @IsEligible BIT;
    DECLARE @IsTransferred BIT;
    DECLARE @Attempt INT;
    DECLARE @SourcePrefix NVARCHAR(500);
    DECLARE @DestPrefix NVARCHAR(500);

    SELECT
        @ClientSampleID = d.ClientSampleID,
        @IsEligible     = d.IsEligibleToTransfer,
        @IsTransferred  = d.IsFileTransferred
    FROM dbo.PGSResultsFileProcessingDetails AS d
    WHERE d.FileProcessingDetailID = @FileProcessingDetailID;

    IF @ClientSampleID IS NULL
    BEGIN
        RAISERROR(N'FileProcessingDetailID %d not found.', 16, 1, @FileProcessingDetailID);
        RETURN;
    END;

    IF ISNULL(@IsEligible, 0) <> 1
    BEGIN
        RAISERROR(N'Sample %s is not eligible to transfer (IsEligibleToTransfer).', 16, 1, @ClientSampleID);
        RETURN;
    END;

    IF ISNULL(@IsTransferred, 0) = 1
    BEGIN
        RAISERROR(N'Sample %s is already marked transferred.', 16, 1, @ClientSampleID);
        RETURN;
    END;

    IF NULLIF(LTRIM(RTRIM(@DestinationRootPath)), N'') IS NULL
    BEGIN
        RAISERROR(N'@DestinationRootPath is required.', 16, 1);
        RETURN;
    END;

    IF NULLIF(LTRIM(RTRIM(@SentrixBarcode)), N'') IS NULL
       OR NULLIF(LTRIM(RTRIM(@SentrixPosition)), N'') IS NULL
    BEGIN
        RAISERROR(N'@SentrixBarcode and @SentrixPosition are required for IDAT file names.', 16, 1);
        RETURN;
    END;

    SET @SourcePrefix = NULLIF(LTRIM(RTRIM(@SourceDirectoryPath)), N'');
    IF @SourcePrefix IS NOT NULL AND RIGHT(@SourcePrefix, 1) <> N'\'
        SET @SourcePrefix = @SourcePrefix + N'\';

    SET @DestPrefix = LTRIM(RTRIM(@DestinationRootPath));
    IF RIGHT(@DestPrefix, 1) <> N'\'
        SET @DestPrefix = @DestPrefix + N'\';

    IF @TransferAttemptNumber IS NULL
    BEGIN
        SELECT @Attempt = ISNULL(MAX(l.TransferAttemptNumber), 0) + 1
        FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
        WHERE l.FileProcessingDetailID = @FileProcessingDetailID;
    END
    ELSE
        SET @Attempt = @TransferAttemptNumber;

    DECLARE @ReportFile NVARCHAR(260) = @ClientSampleID + N'.report.tsv';
    DECLARE @PedFile NVARCHAR(260) = @ClientSampleID + N'.ped';
    DECLARE @IdatRedFile NVARCHAR(260) =
        @SentrixBarcode + N'_' + @SentrixPosition + N'_Red.idat';
    DECLARE @IdatGrnFile NVARCHAR(260) =
        @SentrixBarcode + N'_' + @SentrixPosition + N'_Grn.idat';

    INSERT INTO dbo.PGSResultsFileProcessingSampleFileTransferLog
    (
        FileProcessingDetailID,
        TransferAttemptNumber,
        FileType,
        ExpectedFileName,
        SourceFilePath,
        DestinationFilePath,
        TransferStatus,
        CreatedDate,
        CreatedBy,
        UpdatedDate,
        UpdatedBy
    )
    VALUES
    (
        @FileProcessingDetailID, @Attempt, N'REPORT_TSV', @ReportFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @ReportFile END,
        @DestPrefix + @ReportFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @Attempt, N'PED', @PedFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @PedFile END,
        @DestPrefix + @PedFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @Attempt, N'IDAT_RED', @IdatRedFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @IdatRedFile END,
        @DestPrefix + @IdatRedFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @Attempt, N'IDAT_GRN', @IdatGrnFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @IdatGrnFile END,
        @DestPrefix + @IdatGrnFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    );

    SELECT
        v.SampleFileTransferLogID,
        v.FileProcessingDetailID,
        v.ClientSampleID,
        v.CompositeID,
        v.WGPlateID,
        v.TransferAttemptNumber,
        v.FileType,
        v.ExpectedFileName,
        v.SourceFilePath,
        v.DestinationFilePath,
        v.TransferStatus
    FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog AS v
    WHERE v.FileProcessingDetailID = @FileProcessingDetailID
      AND v.TransferAttemptNumber = @Attempt
    ORDER BY v.FileType;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_UpdateFileResult
(
    @SampleFileTransferLogID INT,
    @TransferStatus          NVARCHAR(20),
    @UpdatedBy               NVARCHAR(22),
    @ErrorMessage            NVARCHAR(500) = NULL,
    @FileSizeBytes           BIGINT        = NULL,
    @SourceFilePath          NVARCHAR(500) = NULL,
    @DestinationFilePath     NVARCHAR(500) = NULL
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();

    IF @TransferStatus NOT IN (N'Pending', N'InProgress', N'Success', N'Failed', N'Skipped')
    BEGIN
        RAISERROR(N'Invalid @TransferStatus.', 16, 1);
        RETURN;
    END;

    UPDATE dbo.PGSResultsFileProcessingSampleFileTransferLog
    SET
        TransferStatus        = @TransferStatus,
        ErrorMessage          = @ErrorMessage,
        FileSizeBytes         = @FileSizeBytes,
        SourceFilePath        = COALESCE(@SourceFilePath, SourceFilePath),
        DestinationFilePath   = COALESCE(@DestinationFilePath, DestinationFilePath),
        TransferStartedDate   = CASE
                                    WHEN @TransferStatus = N'InProgress' AND TransferStartedDate IS NULL THEN @Now
                                    ELSE TransferStartedDate
                                END,
        TransferCompletedDate = CASE
                                    WHEN @TransferStatus IN (N'Success', N'Failed', N'Skipped') THEN @Now
                                    ELSE TransferCompletedDate
                                END,
        UpdatedDate           = @Now,
        UpdatedBy             = @UpdatedBy
    WHERE SampleFileTransferLogID = @SampleFileTransferLogID;

    IF @@ROWCOUNT = 0
    BEGIN
        RAISERROR(N'SampleFileTransferLogID %d not found.', 16, 1, @SampleFileTransferLogID);
        RETURN;
    END;
END;
GO

/*
-- Verification (sample / composite from parent join, not stored on log table):
SELECT *
FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog
WHERE FileProcessingDetailID = 1 AND TransferAttemptNumber = 1;
*/
