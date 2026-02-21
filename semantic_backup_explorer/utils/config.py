"""Centralized configuration for backup operations."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BackupConfig(BaseSettings):  # type: ignore[misc]
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
        Validate that backup drive exists and is accessible.

        Raises:
            ValueError: If backup drive does not exist.
        """
        if not self.backup_drive.exists():
            raise ValueError(f"Backup drive not found: {self.backup_drive}")

        # Note: We used to check writability here by touching a file, but this
        # can fail on Windows drive roots even if the drive is generally writable.
        # Writability will be caught during the actual sync process.
