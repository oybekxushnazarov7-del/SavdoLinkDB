-- S-01: 00_database.sql bo'sh edi — SavdoLinkDB yaratilmasa USE ishlamaydi
IF DB_ID('SavdoLinkDB_v2') IS NULL
    CREATE DATABASE SavdoLinkDB_v2;
GO
USE SavdoLinkDB_v2;
GO
