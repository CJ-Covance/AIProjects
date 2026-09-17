/*
    INSERT scripts for dbo.PGSResultsFileProcessingFinalReportFileDetail

    Creates five rows per sample (NG0029-style files):
      ReportTsvFile, PedFile, RedIdatFile, GrnIdatFile, JSONFile

    FileProcessingDetailID must exist on dbo.PGSResultsFileProcessingDetails.
    ClientSampleID is copied from the parent row (shared field).
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* --------------------------------------------------------------------------
   1. Insert five file rows for one sample
      Set @FileProcessingDetailID, @SentrixBarcode, @SentrixPosition
   -------------------------------------------------------------------------- */
DECLARE @FileProcessingDetailID INT          = 1;
DECLARE @SentrixBarcode         NVARCHAR(50) = N'3991234567';
DECLARE @SentrixPosition        NVARCHAR(50) = N'R01C01';
DECLARE @UserId                 NVARCHAR(22) = N'system';
DECLARE @Now                    DATETIME     = GETDATE();

INSERT INTO dbo.PGSResultsFileProcessingFinalReportFileDetail
(
    FileProcessingDetailID,
    ClientSampleID,
    FileType,
    FileName,
    IsFileExist,
    IsFileTransfered,
    CreatedDate,
    CreatedOn,
    UpdatedDate,
    UpdatedOn,
    TransferDate
)
SELECT
    d.FileProcessingDetailID,
    d.ClientSampleID,
    f.FileType,
    f.FileName,
    0,
    0,
    @Now,
    @UserId,
    @Now,
    @UserId,
    NULL
FROM dbo.PGSResultsFileProcessingDetails AS d
CROSS APPLY (
    VALUES
        (N'ReportTsvFile', d.ClientSampleID + N'.report.tsv'),
        (N'PedFile',       d.ClientSampleID + N'.ped'),
        (N'RedIdatFile',   @SentrixBarcode + N'_' + @SentrixPosition + N'_Red.idat'),
        (N'GrnIdatFile',   @SentrixBarcode + N'_' + @SentrixPosition + N'_Grn.idat'),
        (N'JSONFile',      d.ClientSampleID + N'.json')
) AS f (FileType, FileName)
WHERE d.FileProcessingDetailID = @FileProcessingDetailID
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingFinalReportFileDetail AS x
        WHERE x.FileProcessingDetailID = d.FileProcessingDetailID
          AND x.FileType = f.FileType
      );
GO

/* --------------------------------------------------------------------------
   2. Literal example (uncomment and replace keys)
   -------------------------------------------------------------------------- */
/*
INSERT INTO dbo.PGSResultsFileProcessingFinalReportFileDetail
(
    FileProcessingDetailID,
    ClientSampleID,
    FileType,
    FileName,
    IsFileExist,
    IsFileTransfered,
    CreatedDate,
    CreatedOn,
    UpdatedDate,
    UpdatedOn,
    TransferDate
)
VALUES
    (1, N'SAMPLE001', N'ReportTsvFile', N'SAMPLE001.report.tsv', 1, 0, GETDATE(), N'system', GETDATE(), N'system', NULL),
    (1, N'SAMPLE001', N'PedFile',       N'SAMPLE001.ped',        1, 0, GETDATE(), N'system', GETDATE(), N'system', NULL),
    (1, N'SAMPLE001', N'RedIdatFile',   N'3991234567_R01C01_Red.idat', 1, 0, GETDATE(), N'system', GETDATE(), N'system', NULL),
    (1, N'SAMPLE001', N'GrnIdatFile',   N'3991234567_R01C01_Grn.idat', 1, 0, GETDATE(), N'system', GETDATE(), N'system', NULL),
    (1, N'SAMPLE001', N'JSONFile',      N'SAMPLE001.json',       0, 0, GETDATE(), N'system', GETDATE(), N'system', NULL);
GO
*/

/* --------------------------------------------------------------------------
   3. Bulk insert five file rows for eligible samples that have no final-report rows
   -------------------------------------------------------------------------- */
DECLARE @SentrixBarcode  NVARCHAR(50) = N'3991234567';
DECLARE @SentrixPosition NVARCHAR(50) = N'R01C01';
DECLARE @UserId          NVARCHAR(22) = N'system';
DECLARE @Now             DATETIME     = GETDATE();

INSERT INTO dbo.PGSResultsFileProcessingFinalReportFileDetail
(
    FileProcessingDetailID,
    ClientSampleID,
    FileType,
    FileName,
    IsFileExist,
    IsFileTransfered,
    CreatedDate,
    CreatedOn,
    UpdatedDate,
    UpdatedOn,
    TransferDate
)
SELECT
    d.FileProcessingDetailID,
    d.ClientSampleID,
    f.FileType,
    f.FileName,
    0,
    0,
    @Now,
    @UserId,
    @Now,
    @UserId,
    NULL
FROM dbo.PGSResultsFileProcessingDetails AS d
CROSS APPLY (
    VALUES
        (N'ReportTsvFile', d.ClientSampleID + N'.report.tsv'),
        (N'PedFile',       d.ClientSampleID + N'.ped'),
        (N'RedIdatFile',   @SentrixBarcode + N'_' + @SentrixPosition + N'_Red.idat'),
        (N'GrnIdatFile',   @SentrixBarcode + N'_' + @SentrixPosition + N'_Grn.idat'),
        (N'JSONFile',      d.ClientSampleID + N'.json')
) AS f (FileType, FileName)
WHERE d.IsEligibleToTransfer = 1
  AND ISNULL(d.IsFileTransferred, 0) = 0
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingFinalReportFileDetail AS x
        WHERE x.FileProcessingDetailID = d.FileProcessingDetailID
          AND x.FileType = f.FileType
      );
GO

/* --------------------------------------------------------------------------
   4. Mark a file as existing / transferred
   -------------------------------------------------------------------------- */
/*
UPDATE dbo.PGSResultsFileProcessingFinalReportFileDetail
SET
    IsFileExist      = 1,
    IsFileTransfered = 1,
    TransferDate     = GETDATE(),
    UpdatedDate      = GETDATE(),
    UpdatedOn        = N'system'
WHERE FileProcessingDetailID = 1
  AND FileType = N'ReportTsvFile';
GO
*/

/* --------------------------------------------------------------------------
   5. Verify
   -------------------------------------------------------------------------- */
SELECT
    FinalReportFileDetailID,
    FileProcessingDetailID,
    ClientSampleID,
    FileType,
    FileName,
    IsFileExist,
    IsFileMissing,
    IsFileTransfered,
    CreatedDate,
    CreatedOn,
    UpdatedDate,
    UpdatedOn,
    TransferDate
FROM dbo.PGSResultsFileProcessingFinalReportFileDetail
ORDER BY FileProcessingDetailID, FileType;
GO
