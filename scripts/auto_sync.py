"""Script for automatically synchronizing local folders to a backup location."""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to sys.path to allow imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm

from semantic_backup_explorer.compare.folder_diff import get_folder_content
from semantic_backup_explorer.core.backup_operations import BackupOperations
from semantic_backup_explorer.exceptions import BackupExplorerError
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.sync.sync_missing import sync_files
from semantic_backup_explorer.utils.config import BackupConfig
from semantic_backup_explorer.utils.drive_utils import get_volume_label
from semantic_backup_explorer.utils.index_utils import get_index_metadata
from semantic_backup_explorer.utils.logging_utils import setup_logging


def parse_config(config_path: Path) -> list[str]:
    """
    Parses the markdown config file for source folders.

    Args:
        config_path: Path to the backup configuration file.

    Returns:
        A list of folder paths to synchronize.
    """
    folders = []
    if not config_path.exists():
        return folders
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            # Look for lines starting with '- ' or '* ' followed by a path
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                folder = stripped[2:].strip()
                folders.append(folder)
    return folders


def main() -> None:
    """Main entry point for the auto_sync script."""
    parser = argparse.ArgumentParser(description="Auto Sync local folders to backup.")
    parser.add_argument("--config", default="backup_config.md", help="Path to backup config markdown file.")
    parser.add_argument("--backup_path", help="Path to backup drive/folder root (overrides config).")
    parser.add_argument("--force", action="store_true", help="Force indexing even if drive label mismatches existing index.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)

    # Load Config
    config = BackupConfig()
    if args.backup_path:
        config.backup_drive = Path(args.backup_path)

    try:
        config.validate_backup_drive()
    except Exception as e:
        logger.error(f"Backup drive validation failed: {e}")
        sys.exit(1)

    # 1. Safety check: Verify drive label against existing index
    if config.index_path.exists() and not args.force:
        metadata = get_index_metadata(config.index_path)
        if metadata.label:
            current_label = get_volume_label(config.backup_drive)
            if current_label and current_label != metadata.label:
                logger.error(
                    f"Laufwerks-Konflikt! Der bestehende Index gehört zum Laufwerk '{metadata.label}', "
                    f"aber das angeschlossene Laufwerk hat das Label '{current_label}'."
                )
                logger.error("Bitte schließe das richtige Laufwerk an oder nutze --force zum Überschreiben des Index.")
                sys.exit(1)

    # 2. Scan backup
    logger.info(f"Scanning backup drive at {config.backup_drive}...")
    try:
        scan_backup(config.backup_drive, config.index_path)
    except Exception as e:
        logger.error(f"Error scanning backup drive: {e}")
        sys.exit(1)

    # 2. Load config
    config_file = Path(args.config)
    source_folders = parse_config(config_file)
    if not source_folders:
        logger.warning(f"No source folders found in {args.config}. Please add folders under '## Source Folders' as a list.")
        return

    operations = BackupOperations(index_path=config.index_path)
    results = []

    # 3. Process folders
    for local_path_str in source_folders:
        local_path = Path(local_path_str)
        logger.info(f"Processing {local_path}...")

        if not local_path.exists():
            logger.warning(f"Local path {local_path} does not exist. Skipping.")
            results.append((str(local_path), 0, "Not Found Locally"))
            continue

        result = operations.find_and_compare(local_path)

        if result.error:
            logger.warning(f"Comparison error for {local_path}: {result.error}")
            # If not found in index, we might want to default to creating a new one
            if "No matching backup folder found" in result.error:
                target_root = config.backup_drive / local_path.name
                logger.info(f"Defaulting to new folder: {target_root}")
                files_to_sync = sorted(list(get_folder_content(local_path)))
            else:
                results.append((str(local_path), 0, f"Error: {result.error}"))
                continue
        else:
            target_root = result.backup_path  # type: ignore
            files_to_sync = result.only_local

        if files_to_sync and target_root:
            logger.info(f"Syncing {len(files_to_sync)} files to {target_root}...")

            def sync_callback(current: int, total: int, filename: str, error: Optional[str] = None) -> None:
                if error:
                    tqdm.write(f"  [ERROR] {filename}: {error}")
                else:
                    tqdm.write(f"  [OK] {filename}")
                pbar.update(1)

            with tqdm(total=len(files_to_sync), desc=f"Syncing {local_path.name}", unit="file") as pbar:
                synced, errors = sync_files(files_to_sync, local_path, target_root, callback=sync_callback)

            status = "OK"
            if errors:
                status = f"{len(errors)} errors"
            results.append((str(local_path), len(synced), status))
        else:
            logger.info("Everything up to date.")
            results.append((str(local_path), 0, "Up to date"))

    # 4. Print protocol
    print("\n" + "=" * 60)
    print("BACKUP PROTOCOL")
    print("=" * 60)
    print(f"{'Local Folder':<35} | {'Synced':<8} | {'Status'}")
    print("-" * 60)
    for folder, count, status in results:
        display_folder = folder
        if len(display_folder) > 35:
            display_folder = "..." + display_folder[-32:]
        print(f"{display_folder:<35} | {count:<8} | {status}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except BackupExplorerError as e:
        print(f"Backup Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception("An unexpected error occurred")
        print(f"Unexpected Error: {e}")
        sys.exit(1)
