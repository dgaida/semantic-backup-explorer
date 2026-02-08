import os
from pathlib import Path

def get_folder_content(folder_path):
    """Returns a set of relative file paths in the folder."""
    folder_path = Path(folder_path)
    if not folder_path.exists():
        return set()

    files = set()
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            full_path = Path(root) / f
            files.add(str(full_path.relative_to(folder_path)))
    return files

def compare_folders(local_path, backup_files_list):
    """
    Compares local folder content with a list of files from backup.
    backup_files_list should be relative to the backup folder being compared.
    """
    local_files = get_folder_content(local_path)
    backup_files = set(backup_files_list)

    only_local = local_files - backup_files
    only_backup = backup_files - local_files
    in_both = local_files & backup_files

    return {
        "only_local": sorted(list(only_local)),
        "only_backup": sorted(list(only_backup)),
        "in_both": sorted(list(in_both))
    }
