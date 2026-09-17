/*
    INSERT scripts for dbo.PGSResultsFileProcessingSampleFileTransferLog

    Required:
      - FileProcessingDetailID must exist in dbo.PGSResultsFileProcessingDetails (FK)
      - One row per FileProcessingDetailID (unique constraint)
      - BIT flags: 1 = file exists, 0 = file does not exist
      - CreatedBy / UpdatedBy are required (NVARCHAR(22))

    Do not insert ClientSampleID or CompositeID; those come from the parent via FK.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* --------------------------------------------------------------------------
   1. Single-row insert (replace parameter values)
   -------------------------------------------------------------------------- */
DECLARE @FileProcessingDetailID INT          = 1;          -- existing PK from Details
DECLARE @HasReportTsvFile       BIT          = 1;          -- a. sampleID.report.tsv
DECLARE @HasPedFile             BIT          = 1;          -- b. sampleID.ped
DECLARE @HasRedIdatFile         BIT          = 1;          -- c. *_Red.idat
DECLARE @HasGrnIdatFile         BIT          = 0;          -- d. *_Grn.idat
DECLARE @UserId                 NVARCHAR(22) = N'system';
DECLARE @Now                    DATETIME     = GETDATE();

IF NOT EXISTS (
    SELECT 1
    FROM dbo.PGSResultsFileProcessingDetails AS d
    WHERE d.FileProcessingDetailID = @FileProcessingDetailID
)
BEGIN
    RAISERROR(N'FileProcessingDetailID %d does not exist in PGSResultsFileProcessingDetails.', 16, 1, @FileProcessingDetailID);
END
ELSE IF EXISTS (
    SELECT 1
    FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
    WHERE l.FileProcessingDetailID = @FileProcessingDetailID
)
BEGIN
    RAISERROR(N'A log row already exists for FileProcessingDetailID %d. Use UPDATE instead of INSERT.', 16, 1, @FileProcessingDetailID);
END
ELSE
BEGIN
    INSERT INTO dbo.PGSResultsFileProcessingSampleFileTransferLog
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
        @FileProcessingDetailID,
        @HasReportTsvFile,
        @HasPedFile,
        @HasRedIdatFile,
        @HasGrnIdatFile,
        @Now,
        @UserId,
        @Now,
        @UserId
    );

    SELECT SCOPE_IDENTITY() AS SampleFileTransferLogID;
END;
GO

/* --------------------------------------------------------------------------
   2. Literal insert example (uncomment and set FileProcessingDetailID)
   -------------------------------------------------------------------------- */
/*
INSERT INTO dbo.PGSResultsFileProcessingSampleFileTransferLog
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
SELECT
    d.FileProcessingDetailID,
    1,  -- HasReportTsvFile
    1,  -- HasPedFile
    1,  -- HasRedIdatFile
    1,  -- HasGrnIdatFile
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
FROM dbo.PGSResultsFileProcessingDetails AS d
WHERE d.FileProcessingDetailID = 1
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
        WHERE l.FileProcessingDetailID = d.FileProcessingDetailID
      );
GO
*/

/* --------------------------------------------------------------------------
   3. Bulk insert for eligible samples that do not yet have a log row
      (all four existence flags default to 0 until the scan updates them)
   -------------------------------------------------------------------------- */
INSERT INTO dbo.PGSResultsFileProcessingSampleFileTransferLog
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
SELECT
    d.FileProcessingDetailID,
    0,
    0,
    0,
    0,
    GETDATE(),
    N'system',
    GETDATE(),
    N'system'
FROM dbo.PGSResultsFileProcessingDetails AS d
WHERE d.IsEligibleToTransfer = 1
  AND ISNULL(d.IsFileTransferred, 0) = 0
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
        WHERE l.FileProcessingDetailID = d.FileProcessingDetailID
      );
GO

/* --------------------------------------------------------------------------
   4. Update existing log row (use when unique FK already has a row)
   -------------------------------------------------------------------------- */
/*
UPDATE l
SET
    l.HasReportTsvFile = 1,
    l.HasPedFile       = 1,
    l.HasRedIdatFile   = 1,
    l.HasGrnIdatFile   = 1,
    l.UpdatedDate      = GETDATE(),
    l.UpdatedBy        = N'system'
FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
WHERE l.FileProcessingDetailID = 1;
GO
*/

/* --------------------------------------------------------------------------
   5. Verify
   -------------------------------------------------------------------------- */
SELECT
    l.SampleFileTransferLogID,
    l.FileProcessingDetailID,
    d.ClientSampleID,
    d.CompositeID,
    l.HasReportTsvFile,
    l.HasPedFile,
    l.HasRedIdatFile,
    l.HasGrnIdatFile,
    l.CreatedDate,
    l.CreatedBy
FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
INNER JOIN dbo.PGSResultsFileProcessingDetails AS d
    ON d.FileProcessingDetailID = l.FileProcessingDetailID
ORDER BY l.SampleFileTransferLogID;
GO
