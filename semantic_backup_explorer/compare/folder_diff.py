import os
from pathlib import Path


def get_folder_content(folder_path):
    """Returns a dictionary of relative file paths and their mtimes."""
    folder_path = Path(folder_path)
    if not folder_path.exists():
        return {}

    files = {}
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            full_path = Path(root) / f
            rel_path = str(full_path.relative_to(folder_path))
            try:
                files[rel_path] = os.path.getmtime(full_path)
            except Exception:
                files[rel_path] = 0.0
    return files


def compare_folders(local_path, backup_files):
    """
    Compares local folder content with backup files.
    backup_files can be a list of relative paths or a dict of {rel_path: mtime}.
    """
    local_files_dict = get_folder_content(local_path)
    local_paths = set(local_files_dict.keys())

    if isinstance(backup_files, dict):
        backup_paths = set(backup_files.keys())
    else:
        backup_paths = set(backup_files)

    only_local = local_paths - backup_paths
    only_backup = backup_paths - local_paths
    in_both = local_paths & backup_paths

    # Check for newer files in local
    newer_locally = set()
    if isinstance(backup_files, dict):
        for path in in_both:
            local_mtime = local_files_dict.get(path, 0.0)
            backup_mtime = backup_files.get(path, 0.0)
            # Use a small epsilon for float comparison (0.1 seconds)
            if local_mtime > backup_mtime + 0.1:
                newer_locally.add(path)

    only_local.update(newer_locally)
    in_both = in_both - newer_locally

    return {"only_local": sorted(list(only_local)), "only_backup": sorted(list(only_backup)), "in_both": sorted(list(in_both))}
