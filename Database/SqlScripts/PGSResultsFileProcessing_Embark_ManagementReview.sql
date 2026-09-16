/*
    Embark / Management Failure Review – PGS Results File Processing
    Tables: dbo.PGSResultsFileProcessing, dbo.PGSResultsFileProcessingDetails

    Supports:
      - Listing non-transferred specimens for management review (AC 1, 4 – data layer)
      - Marking specimens ineligible for Embark data delivery after Release To Billing (AC 7d)

    Does NOT implement (requires other lab/specimen/message tables):
      - AC 2, 3, 5 (UI)
      - AC 6a (Find Redo routing)
      - AC 7a, 7b, 7c (Complete, Report Date, LabProcessingFailureFinal message)
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* ============================================================================
   1. Foreign key (not present in supplied DDL; required for referential integrity)
   ============================================================================ */
IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = N'FK_PGSResultsFileProcessingDetails_PGSResultsFileProcessing'
)
BEGIN
    ALTER TABLE dbo.PGSResultsFileProcessingDetails WITH CHECK
    ADD CONSTRAINT FK_PGSResultsFileProcessingDetails_PGSResultsFileProcessing
        FOREIGN KEY (FileProcessingID)
        REFERENCES dbo.PGSResultsFileProcessing (FileProcessingID);
END;
GO

/* ============================================================================
   2. Indexes
   ============================================================================ */
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileProcessingDetails_FileProcessingID'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessingDetails')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileProcessingDetails_FileProcessingID
        ON dbo.PGSResultsFileProcessingDetails (FileProcessingID)
        INCLUDE (
            ClientSampleID,
            IsEligibleToTransfer,
            IsFileTransferred,
            InEligibilityReason,
            UpdatedDate
        );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileProcessingDetails_ClientSampleID'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessingDetails')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileProcessingDetails_ClientSampleID
        ON dbo.PGSResultsFileProcessingDetails (ClientSampleID)
        INCLUDE (
            FileProcessingID,
            IsEligibleToTransfer,
            IsFileTransferred,
            InEligibilityReason,
            FileProcessingDetailID,
            UpdatedDate
        );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PGSResultsFileProcessing_WGPlateID'
      AND object_id = OBJECT_ID(N'dbo.PGSResultsFileProcessing')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PGSResultsFileProcessing_WGPlateID
        ON dbo.PGSResultsFileProcessing (WGPlateID)
        INCLUDE (FileProcessingID, ScanForEligibilityDate, TransferredDate);
END;
GO

/* ============================================================================
   3. List specimens for Management Failure Review (Failed Call Rate context)
      AC 1, 4 – Embark PGS pipeline specimens not yet transferred; optional filters.
   ============================================================================ */
CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingDetails_GetFailedCallRateManagementReview
(
    @WGPlateID              NVARCHAR(28)  = NULL,
    @InEligibilityReason    NVARCHAR(150) = NULL,
    @OnlyIneligible         BIT           = 1,
    @IncludePendingEligibility BIT        = 1
)
AS
BEGIN
    SET NOCOUNT ON;

    /*
        Business rules (PGS tables only):
        - Exclude rows already transferred to Embark (data delivery complete).
        - Default: include failed / ineligible transfer rows (IsEligibleToTransfer = 0)
          and optionally rows not yet evaluated (IsEligibleToTransfer IS NULL).
        - One row per ClientSampleID (latest detail by UpdatedDate) to avoid join duplicates.
    */
    ;WITH RankedDetails AS
    (
        SELECT
            d.FileProcessingDetailID,
            d.FileProcessingID,
            d.ClientSampleID,
            d.CompositeID,
            d.IsSplitFileSuccessful,
            d.IsEligibleToTransfer,
            d.IsFileTransferred,
            d.InEligibilityReason,
            d.IsPriorityTransfer,
            d.TransferredDate      AS DetailTransferredDate,
            d.CreatedDate,
            d.UpdatedDate,
            h.WGPlateID,
            h.FileProcessingDate,
            h.ScanForEligibilityDate,
            h.TransferredDate      AS HeaderTransferredDate,
            h.ErrorMessage         AS HeaderErrorMessage,
            ROW_NUMBER() OVER (
                PARTITION BY d.ClientSampleID
                ORDER BY d.UpdatedDate DESC, d.FileProcessingDetailID DESC
            ) AS rn
        FROM dbo.PGSResultsFileProcessingDetails AS d
        INNER JOIN dbo.PGSResultsFileProcessing AS h
            ON h.FileProcessingID = d.FileProcessingID
        WHERE ISNULL(d.IsFileTransferred, 0) = 0
          AND (@WGPlateID IS NULL OR h.WGPlateID = @WGPlateID)
          AND (
                @InEligibilityReason IS NULL
                OR d.InEligibilityReason = @InEligibilityReason
              )
          AND (
                (@OnlyIneligible = 0)
                OR (d.IsEligibleToTransfer = 0)
                OR (
                    @IncludePendingEligibility = 1
                    AND d.IsEligibleToTransfer IS NULL
                   )
              )
    )
    SELECT
        FileProcessingDetailID,
        FileProcessingID,
        ClientSampleID,
        CompositeID,
        IsSplitFileSuccessful,
        IsEligibleToTransfer,
        IsFileTransferred,
        InEligibilityReason,
        IsPriorityTransfer,
        DetailTransferredDate,
        CreatedDate,
        UpdatedDate,
        WGPlateID,
        FileProcessingDate,
        ScanForEligibilityDate,
        HeaderTransferredDate,
        HeaderErrorMessage
    FROM RankedDetails
    WHERE rn = 1
    ORDER BY WGPlateID, ClientSampleID;
END;
GO

/* ============================================================================
   4. Release To Billing – exclude from Embark data delivery (AC 7d)
   ============================================================================ */
CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessingDetails_SetEmbarkDataDeliveryIneligible
(
    @ClientSampleID       NVARCHAR(36),
    @UpdatedBy            NVARCHAR(22),
    @InEligibilityReason  NVARCHAR(150) = N'Not eligible for Embark data delivery - Release To Billing'
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();
    DECLARE @RowsUpdated INT;

    IF NULLIF(LTRIM(RTRIM(@ClientSampleID)), N'') IS NULL
    BEGIN
        RAISERROR(N'@ClientSampleID is required.', 16, 1);
        RETURN;
    END;

    IF NULLIF(LTRIM(RTRIM(@UpdatedBy)), N'') IS NULL
    BEGIN
        RAISERROR(N'@UpdatedBy is required.', 16, 1);
        RETURN;
    END;

    UPDATE d
    SET
        d.IsEligibleToTransfer = 0,
        d.InEligibilityReason  = @InEligibilityReason,
        d.UpdatedDate          = @Now,
        d.UpdatedBy            = @UpdatedBy
    FROM dbo.PGSResultsFileProcessingDetails AS d
    WHERE d.ClientSampleID = @ClientSampleID
      AND ISNULL(d.IsFileTransferred, 0) = 0;

    SET @RowsUpdated = @@ROWCOUNT;

    SELECT
        @RowsUpdated AS RowsUpdated,
        @ClientSampleID AS ClientSampleID,
        CAST(0 AS BIT) AS IsEligibleToTransfer,
        @InEligibilityReason AS InEligibilityReason;
END;
GO

/* ============================================================================
   5. Record eligibility scan completion on plate header
   ============================================================================ */
CREATE OR ALTER PROCEDURE dbo.usp_PGSResultsFileProcessing_SetScanForEligibilityDate
(
    @FileProcessingID INT,
    @UpdatedBy        NVARCHAR(22),
    @ScanDate         DATETIME = NULL
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Now DATETIME = GETDATE();
    SET @ScanDate = ISNULL(@ScanDate, @Now);

    IF @FileProcessingID IS NULL
    BEGIN
        RAISERROR(N'@FileProcessingID is required.', 16, 1);
        RETURN;
    END;

    UPDATE dbo.PGSResultsFileProcessing
    SET
        ScanForEligibilityDate = @ScanDate,
        UpdatedDate            = @Now,
        UpdatedBy              = @UpdatedBy
    WHERE FileProcessingID = @FileProcessingID;

    IF @@ROWCOUNT = 0
    BEGIN
        RAISERROR(N'FileProcessingID %d not found.', 16, 1, @FileProcessingID);
        RETURN;
    END;
END;
GO

/* ============================================================================
   6. Sample execution
   ============================================================================ */
/*
EXEC dbo.usp_PGSResultsFileProcessingDetails_GetFailedCallRateManagementReview
    @WGPlateID = NULL,
    @InEligibilityReason = NULL,
    @OnlyIneligible = 1,
    @IncludePendingEligibility = 1;

EXEC dbo.usp_PGSResultsFileProcessingDetails_SetEmbarkDataDeliveryIneligible
    @ClientSampleID = N'<SampleId>',
    @UpdatedBy = N'<UserId>';

EXEC dbo.usp_PGSResultsFileProcessing_SetScanForEligibilityDate
    @FileProcessingID = 1,
    @UpdatedBy = N'<UserId>';
*/
