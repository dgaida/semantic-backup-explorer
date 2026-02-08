@echo off
setlocal

:: Ensure the working directory is the folder where the script is located
cd /d "%~dp0"

:: --- CONFIGURATION ---
:: Set your backup drive letter here (e.g., E:)
:: NOTE: Do NOT use a trailing backslash here to avoid issues with quote escaping
set "BACKUP_DRIVE=E:"
:: Set the path to your configuration file
set "CONFIG_FILE=backup_config.md"
:: ---------------------

title Semantic Backup Explorer - Monthly Sync

echo ============================================================
echo           SEMANTIC BACKUP EXPLORER - AUTO SYNC
echo ============================================================
echo.
echo IMPORTANT: Please ensure your backup hard disk drive
echo is connected to the computer.
echo.
echo Target Drive: %BACKUP_DRIVE%\
echo.
pause

if not exist "%BACKUP_DRIVE%\" (
    echo ERROR: Backup drive %BACKUP_DRIVE%\ not found!
    echo Please connect the drive and try again.
    pause
    exit /b 1
)

echo.
echo [1/2] Starting backup drive indexing and synchronization...
:: We append a backslash to the path here to ensure it's treated as a directory root
python scripts/auto_sync.py --config "%CONFIG_FILE%" --backup_path "%BACKUP_DRIVE%\\"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: The backup script encountered an error.
) else (
    echo.
    echo [2/2] Backup process completed successfully.
)

echo.
echo Press any key to exit.
pause

:: ============================================================================
:: HOW TO SCHEDULE THIS TASK ONCE A MONTH:
::
:: 1. Open "Command Prompt" as Administrator.
:: 2. Run the following command (replace [PATH_TO_BATCH] with the full path to this file):
::
::    schtasks /create /tn "MonthlyBackup" /tr "[PATH_TO_BATCH]" /sc monthly /d 1 /st 10:00
::
:: This will run the backup on the 1st of every month at 10:00 AM.
:: ============================================================================
