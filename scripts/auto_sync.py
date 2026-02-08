import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm

from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.sync.sync_missing import sync_files
from semantic_backup_explorer.utils.index_utils import find_backup_folder, get_all_files_from_index


def parse_config(config_path):
    """Parses the markdown config file for source folders."""
    folders = []
    if not os.path.exists(config_path):
        return folders
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            # Look for lines starting with '- ' followed by a path
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                folder = line.strip()[2:].strip()
                folders.append(folder)
    return folders


def main():
    parser = argparse.ArgumentParser(description="Auto Sync local folders to backup.")
    parser.add_argument("--config", default="backup_config.md", help="Path to backup config markdown file.")
    parser.add_argument("--backup_path", required=True, help="Path to backup drive/folder root.")
    args = parser.parse_args()

    index_path = "data/backup_index.md"
    os.makedirs("data", exist_ok=True)

    # 1. Scan backup
    print(f"Scanning backup drive at {args.backup_path}...")
    try:
        scan_backup(args.backup_path, index_path)
    except Exception as e:
        print(f"Error scanning backup drive: {e}")
        sys.exit(1)

    # 2. Load config
    source_folders = parse_config(args.config)
    if not source_folders:
        print(f"No source folders found in {args.config}. Please add folders under '## Source Folders' as a list.")
        return

    results = []

    # 3. Process folders
    for local_path in source_folders:
        print(f"\nProcessing {local_path}...")
        if not os.path.exists(local_path):
            print(f"Warning: Local path {local_path} does not exist. Skipping.")
            results.append((local_path, 0, "Not Found Locally"))
            continue

        # Determine folder name for matching
        folder_name = Path(local_path).name
        if not folder_name:  # Handle root drives or trailing slashes
            folder_name = str(Path(local_path)).replace(":", "").replace("\\", "_").replace("/", "_")

        backup_folder = find_backup_folder(folder_name, index_path)

        if backup_folder:
            print(f"Found matching backup folder in index: {backup_folder}")
            backup_files = get_all_files_from_index(backup_folder, index_path)
            diff = compare_folders(local_path, backup_files)
            files_to_sync = diff["only_local"]
            target_root = backup_folder
        else:
            print(f"No matching backup folder found for '{folder_name}'.")
            # Default to backup_path / folder_name if not found in index
            target_root = os.path.join(args.backup_path, folder_name)
            print(f"Will sync to new folder: {target_root}")
            # For a new folder, all local files are considered missing in backup
            from semantic_backup_explorer.compare.folder_diff import get_folder_content

            files_to_sync = sorted(list(get_folder_content(local_path)))

        if files_to_sync:
            print(f"Syncing {len(files_to_sync)} files...")
            with tqdm(total=len(files_to_sync), desc=f"Syncing {folder_name}", unit="file") as pbar:
                synced, errors = sync_files(
                    files_to_sync, local_path, target_root, callback=lambda current, total, filename: pbar.update(1)
                )
            status = "OK"
            if errors:
                status = f"{len(errors)} errors"
            results.append((local_path, len(synced), status))
        else:
            print("Everything up to date.")
            results.append((local_path, 0, "Up to date"))

    # 4. Print protocol
    print("\n" + "=" * 60)
    print("BACKUP PROTOCOL")
    print("=" * 60)
    print(f"{'Local Folder':<35} | {'Synced':<8} | {'Status'}")
    print("-" * 60)
    for folder, count, status in results:
        # Truncate folder name if too long
        display_folder = folder
        if len(display_folder) > 35:
            display_folder = "..." + display_folder[-32:]
        print(f"{display_folder:<35} | {count:<8} | {status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
