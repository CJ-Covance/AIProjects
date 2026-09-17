/*
    Logger: Embark Results Service file transfer per eligible sample.

    For each selected eligible sample (PGSResultsFileProcessingDetails), up to four
    files are transferred using the sample's .ped composite identifier (CompositeID):
      a. {sampleID}.report.tsv
      b. {sampleID}.ped
      c. {sentrixbarcode}_{sentrixposition}_Red.idat
      d. {sentrixbarcode}_{sentrixposition}_Grn.idat

    One log row per file per transfer attempt (typically four rows per attempt).
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.PGSResultsFileProcessingSampleFileTransferLog
    (
        SampleFileTransferLogID   INT            IDENTITY(1, 1) NOT NULL,
        FileProcessingDetailID    INT            NOT NULL,
        ClientSampleID            NVARCHAR(36)   NOT NULL,
        CompositeID               NVARCHAR(60)   NULL,
        TransferAttemptNumber     INT            NOT NULL
            CONSTRAINT DF_PGSResultsFileTransferLog_TransferAttemptNumber DEFAULT (1),
        FileType                  NVARCHAR(20)   NOT NULL,
        ExpectedFileName          NVARCHAR(260)  NOT NULL,
        SourceFilePath            NVARCHAR(500)  NULL,
        DestinationRootPath       NVARCHAR(500)  NULL,
        DestinationFilePath       NVARCHAR(500)  NULL,
        TransferStatus            NVARCHAR(20)   NOT NULL
            CONSTRAINT DF_PGSResultsFileTransferLog_TransferStatus DEFAULT (N'Pending'),
        ErrorMessage              NVARCHAR(500)  NULL,
        FileSizeBytes             BIGINT         NULL,
        TransferStartedDate       DATETIME       NULL,
        TransferCompletedDate     DATETIME       NULL,
        CreatedDate               DATETIME       NOT NULL
            CONSTRAINT DF_PGSResultsFileTransferLog_CreatedDate DEFAULT (GETDATE()),
        CreatedBy                 NVARCHAR(22)   NOT NULL,
        UpdatedDate               DATETIME       NOT NULL
            CONSTRAINT DF_PGSResultsFileTransferLog_UpdatedDate DEFAULT (GETDATE()),
        UpdatedBy                   NVARCHAR(22)   NOT NULL,

        CONSTRAINT PK_PGSResultsFileProcessingSampleFileTransferLog
            PRIMARY KEY CLUSTERED (SampleFileTransferLogID ASC),

        CONSTRAINT FK_PGSResultsFileTransferLog_FileProcessingDetail
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
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileTransferLog_ClientSampleID_Attempt'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_ClientSampleID_Attempt
        ON dbo.PGSResultsFileProcessingSampleFileTransferLog (ClientSampleID, TransferAttemptNumber)
        INCLUDE (FileType, TransferStatus, ExpectedFileName, TransferCompletedDate);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileTransferLog_CompositeID'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_CompositeID
        ON dbo.PGSResultsFileProcessingSampleFileTransferLog (CompositeID)
        WHERE CompositeID IS NOT NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileTransferLog_Status_Pending'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessingSampleFileTransferLog')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileTransferLog_Status_Pending
        ON dbo.PGSResultsFileProcessingSampleFileTransferLog (TransferStatus, FileProcessingDetailID)
        WHERE TransferStatus IN (N'Pending', N'InProgress');
END;
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
    DECLARE @CompositeID NVARCHAR(60);
    DECLARE @IsEligible BIT;
    DECLARE @IsTransferred BIT;
    DECLARE @Attempt INT;
    DECLARE @SourcePrefix NVARCHAR(500);

    SELECT
        @ClientSampleID = d.ClientSampleID,
        @CompositeID    = d.CompositeID,
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
        ClientSampleID,
        CompositeID,
        TransferAttemptNumber,
        FileType,
        ExpectedFileName,
        SourceFilePath,
        DestinationRootPath,
        DestinationFilePath,
        TransferStatus,
        CreatedDate,
        CreatedBy,
        UpdatedDate,
        UpdatedBy
    )
    VALUES
    (
        @FileProcessingDetailID, @ClientSampleID, @CompositeID, @Attempt, N'REPORT_TSV', @ReportFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @ReportFile END,
        @DestinationRootPath,
        @DestinationRootPath + CASE WHEN RIGHT(@DestinationRootPath, 1) = N'\' THEN N'' ELSE N'\' END + @ReportFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @ClientSampleID, @CompositeID, @Attempt, N'PED', @PedFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @PedFile END,
        @DestinationRootPath,
        @DestinationRootPath + CASE WHEN RIGHT(@DestinationRootPath, 1) = N'\' THEN N'' ELSE N'\' END + @PedFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @ClientSampleID, @CompositeID, @Attempt, N'IDAT_RED', @IdatRedFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @IdatRedFile END,
        @DestinationRootPath,
        @DestinationRootPath + CASE WHEN RIGHT(@DestinationRootPath, 1) = N'\' THEN N'' ELSE N'\' END + @IdatRedFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    ),
    (
        @FileProcessingDetailID, @ClientSampleID, @CompositeID, @Attempt, N'IDAT_GRN', @IdatGrnFile,
        CASE WHEN @SourcePrefix IS NULL THEN NULL ELSE @SourcePrefix + @IdatGrnFile END,
        @DestinationRootPath,
        @DestinationRootPath + CASE WHEN RIGHT(@DestinationRootPath, 1) = N'\' THEN N'' ELSE N'\' END + @IdatGrnFile,
        N'Pending', @Now, @CreatedBy, @Now, @CreatedBy
    );

    SELECT
        SampleFileTransferLogID,
        FileProcessingDetailID,
        ClientSampleID,
        CompositeID,
        TransferAttemptNumber,
        FileType,
        ExpectedFileName,
        SourceFilePath,
        DestinationFilePath,
        TransferStatus
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog
    WHERE FileProcessingDetailID = @FileProcessingDetailID
      AND TransferAttemptNumber = @Attempt
    ORDER BY FileType;
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

/* ============================================================================
   Sample data (illustrative — run only in non-production)
   ============================================================================ */
/*
DECLARE @DetailId INT = 1;

EXEC dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_InitializeAttempt
    @FileProcessingDetailID = @DetailId,
    @DestinationRootPath      = N'\\embark-results\source\incoming\',
    @SentrixBarcode         = N'3991234567',
    @SentrixPosition        = N'R01C01',
    @CreatedBy              = N'system',
    @SourceDirectoryPath    = N'D:\Lab\PGS\Plate001\';

-- After each file copy:
EXEC dbo.usp_PGSResultsFileProcessingSampleFileTransferLog_UpdateFileResult
    @SampleFileTransferLogID = 1,
    @TransferStatus          = N'Success',
    @UpdatedBy               = N'system',
    @FileSizeBytes           = 102400;
*/

/* ============================================================================
   Verification: four file types per attempt; names match requirement pattern
   ============================================================================ */
/*
SELECT
    l.ClientSampleID,
    l.CompositeID,
    l.TransferAttemptNumber,
    l.FileType,
    l.ExpectedFileName,
    l.TransferStatus,
    l.DestinationFilePath
FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
WHERE l.FileProcessingDetailID = @DetailId
  AND l.TransferAttemptNumber = 1;

-- Expect exactly 4 rows: REPORT_TSV, PED, IDAT_RED, IDAT_GRN
SELECT FileProcessingDetailID, TransferAttemptNumber, COUNT(*) AS FileCount
FROM dbo.PGSResultsFileProcessingSampleFileTransferLog
GROUP BY FileProcessingDetailID, TransferAttemptNumber
HAVING COUNT(*) <> 4;
*/
