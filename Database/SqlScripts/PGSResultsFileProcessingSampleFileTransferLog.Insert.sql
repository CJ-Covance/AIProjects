/*
    INSERT scripts for client-driven file existence log.

    1) Catalog: dbo.PGSClientRequiredFileType  (NG0029 seeded in table script)
    2) Log:     dbo.PGSResultsFileProcessingSampleFileTransferLog
                one row per required file type for the sample (FK to catalog)
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* --------------------------------------------------------------------------
   1. Ensure NG0029 required files exist (safe to re-run)
   -------------------------------------------------------------------------- */
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
SELECT src.ClientID, src.FileTypeCode, src.FileDescription, src.FileNamePattern,
       src.DisplaySequence, 1, GETDATE(), N'system', GETDATE(), N'system'
FROM (
    VALUES
        (N'NG0029', N'REPORT_TSV', N'sampleID.report.tsv',                         N'{ClientSampleID}.report.tsv',                    1),
        (N'NG0029', N'PED',        N'sampleID.ped',                                N'{ClientSampleID}.ped',                           2),
        (N'NG0029', N'IDAT_RED',   N'sentrixbarcode_sentrixposition_Red.idat',     N'{SentrixBarcode}_{SentrixPosition}_Red.idat',    3),
        (N'NG0029', N'IDAT_GRN',   N'sentrixbarcode_sentrixposition_Grn.idat',     N'{SentrixBarcode}_{SentrixPosition}_Grn.idat',    4),
        (N'NG0029', N'JSONFile',   N'sampleID.json',                               N'{ClientSampleID}.json',                          5)
) AS src (ClientID, FileTypeCode, FileDescription, FileNamePattern, DisplaySequence)
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.PGSClientRequiredFileType AS ft
    WHERE ft.ClientID = src.ClientID
      AND ft.FileTypeCode = src.FileTypeCode
);
GO

/* --------------------------------------------------------------------------
   2. Insert log rows for one sample using NG0029 file types (dynamic)
      Replace @FileProcessingDetailID with an existing Details PK.
   -------------------------------------------------------------------------- */
DECLARE @FileProcessingDetailID INT          = 1;
DECLARE @ClientID               NVARCHAR(20) = N'NG0029';
DECLARE @UserId                 NVARCHAR(22) = N'system';
DECLARE @Now                    DATETIME     = GETDATE();

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
    d.FileProcessingDetailID,
    ft.ClientRequiredFileTypeID,
    0,
    @Now,
    @UserId,
    @Now,
    @UserId
FROM dbo.PGSResultsFileProcessingDetails AS d
INNER JOIN dbo.PGSClientRequiredFileType AS ft
    ON ft.ClientID = @ClientID
   AND ft.IsActive = 1
WHERE d.FileProcessingDetailID = @FileProcessingDetailID
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
        WHERE l.FileProcessingDetailID = d.FileProcessingDetailID
          AND l.ClientRequiredFileTypeID = ft.ClientRequiredFileTypeID
      );
GO

/* --------------------------------------------------------------------------
   3. Set existence flags for an NG0029 sample (example)
   -------------------------------------------------------------------------- */
DECLARE @FileProcessingDetailID INT          = 1;
DECLARE @ClientID               NVARCHAR(20) = N'NG0029';
DECLARE @UserId                 NVARCHAR(22) = N'system';
DECLARE @Now                    DATETIME     = GETDATE();

UPDATE l
SET
    l.FileExists  = CASE ft.FileTypeCode
                        WHEN N'REPORT_TSV' THEN 1
                        WHEN N'PED'        THEN 1
                        WHEN N'IDAT_RED'   THEN 1
                        WHEN N'IDAT_GRN'   THEN 0
                        ELSE l.FileExists
                    END,
    l.UpdatedDate = @Now,
    l.UpdatedBy   = @UserId
FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
INNER JOIN dbo.PGSClientRequiredFileType AS ft
    ON ft.ClientRequiredFileTypeID = l.ClientRequiredFileTypeID
WHERE l.FileProcessingDetailID = @FileProcessingDetailID
  AND ft.ClientID = @ClientID;
GO

/* --------------------------------------------------------------------------
   4. Bulk initialize log rows for eligible samples (client NG0029)
   -------------------------------------------------------------------------- */
DECLARE @ClientID NVARCHAR(20) = N'NG0029';
DECLARE @UserId   NVARCHAR(22) = N'system';
DECLARE @Now      DATETIME     = GETDATE();

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
    d.FileProcessingDetailID,
    ft.ClientRequiredFileTypeID,
    0,
    @Now,
    @UserId,
    @Now,
    @UserId
FROM dbo.PGSResultsFileProcessingDetails AS d
INNER JOIN dbo.PGSClientRequiredFileType AS ft
    ON ft.ClientID = @ClientID
   AND ft.IsActive = 1
WHERE d.IsEligibleToTransfer = 1
  AND ISNULL(d.IsFileTransferred, 0) = 0
  AND NOT EXISTS (
        SELECT 1
        FROM dbo.PGSResultsFileProcessingSampleFileTransferLog AS l
        WHERE l.FileProcessingDetailID = d.FileProcessingDetailID
          AND l.ClientRequiredFileTypeID = ft.ClientRequiredFileTypeID
      );
GO

/* --------------------------------------------------------------------------
   5. Verify NG0029 (pivoted flags + normalized rows)
   -------------------------------------------------------------------------- */
SELECT *
FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog_NG0029;

SELECT
    v.FileProcessingDetailID,
    v.ClientSampleID,
    v.ClientID,
    v.FileTypeCode,
    v.FileDescription,
    v.FileExists
FROM dbo.vw_PGSResultsFileProcessingSampleFileTransferLog AS v
WHERE v.ClientID = N'NG0029'
ORDER BY v.FileProcessingDetailID, v.DisplaySequence;
GO
