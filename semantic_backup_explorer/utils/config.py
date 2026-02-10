"""Centralized configuration for backup operations."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BackupConfig(BaseSettings):
    """
    Central configuration for backup operations.

    Loads values from environment variables or a .env file.
    """

    backup_drive: Path = Path("/media/backup")
    index_path: Path = Path("data/backup_index.md")
    embeddings_path: Path = Path("data/embeddings")
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def validate_backup_drive(self) -> None:
        """
        Validate that backup drive exists and is writable.

        Raises:
            ValueError: If backup drive does not exist.
            PermissionError: If backup drive is not writable.
        """
        if not self.backup_drive.exists():
            raise ValueError(f"Backup drive not found: {self.backup_drive}")

        # Test write
        test_file = self.backup_drive / ".backup_test"
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError as e:
            raise PermissionError(f"Backup drive not writable: {self.backup_drive}") from e
