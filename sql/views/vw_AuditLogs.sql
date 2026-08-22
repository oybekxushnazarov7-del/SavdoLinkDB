CREATE OR ALTER VIEW audit.vw_AuditLogs AS
SELECT 
    e.ErrorLogId,
    e.LoadId,
    e.ErrorNumber,
    e.ErrorMessage,
    e.ErrorLine,
    e.ErrorProcedure
FROM audit.ErrorLog e;
GO