

IF OBJECT_ID('audit.LoadLog','U') is null 
Begin
    CREATE TABLE audit.LoadLog (
        LoadLogId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        StartedAt DATETIME2(0) NOT NULL,
        FinishedAt DATETIME2(0) NULL,
        RowsRead INT NULL,
        RowsValid INT NULL,
        RowsRejected INT NULL,
        RowsLoaded INT NULL,
        Status NVARCHAR(20) NOT NULL,
        Message NVARCHAR(1000) NULL,

        CONSTRAINT PK_LoadLog PRIMARY KEY CLUSTERED (LoadLogId),
        CONSTRAINT CK_LoadLog_Status CHECK (Status IN ('RUNNING', 'SUCCESS', 'FAILED'))
    );
END

IF OBJECT_ID('audit.ErrorLog','U') is null 
Begin
    CREATE TABLE audit.ErrorLog (
        ErrorLogId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NULL,
        ErrorNumber INT NULL,
        ErrorLine INT NULL,
        ErrorMessage NVARCHAR(2000) NULL,
        ErrorProcedure NVARCHAR(200) NULL,
        LoggedAt DATETIME2(0) NOT NULL CONSTRAINT DF_ErrorLog_LoggedAt DEFAULT SYSDATETIME(),

        CONSTRAINT PK_ErrorLog PRIMARY KEY CLUSTERED (ErrorLogId)
    );
END

IF OBJECT_ID('audit.ProductHistory','U') is null 
Begin
    CREATE TABLE audit.ProductHistory (
        HistoryId BIGINT IDENTITY(1,1) NOT NULL,
        ProductId INT NOT NULL,
        ChangeType NVARCHAR(10) NOT NULL,
        OldName NVARCHAR(200) NULL,
        NewName NVARCHAR(200) NULL,
        ChangedAt DATETIME2(0) NOT NULL CONSTRAINT DF_ProductHistory_ChangedAt DEFAULT SYSDATETIME(),

        CONSTRAINT PK_ProductHistory PRIMARY KEY CLUSTERED (HistoryId),
        CONSTRAINT CK_ProductHistory_ChangeType CHECK (ChangeType IN ('UPDATE', 'DELETE'))
    );
END
USE SavdoLinkDB_v2;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.columns 
    WHERE object_id = OBJECT_ID('audit.ProductHistory') AND name = 'OldUnitPrice'
)
BEGIN
    ALTER TABLE audit.ProductHistory
    ADD OldUnitPrice DECIMAL(18,2) NULL,
        NewUnitPrice DECIMAL(18,2) NULL;
END;
GO