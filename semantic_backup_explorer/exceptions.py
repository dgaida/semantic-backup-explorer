"""Custom exceptions for the Semantic Backup Explorer."""


class BackupExplorerError(Exception):
    """Base exception for all backup explorer errors."""

    pass


class BackupDriveNotFoundError(BackupExplorerError):
    """Raised when backup drive is not accessible."""

    pass


class IndexCorruptedError(BackupExplorerError):
    """Raised when backup index is corrupted or unreadable."""

    pass


class SyncError(BackupExplorerError):
    """Raised when file synchronization fails."""

    def __init__(self, failed_files: list[tuple[str, str]], *args: object):
        self.failed_files = failed_files
        super().__init__(*args)
