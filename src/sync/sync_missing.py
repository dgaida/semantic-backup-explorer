import shutil
from pathlib import Path

def sync_files(files_to_sync, source_root, target_root):
    """
    Copies files from source_root to target_root.
    files_to_sync is a list of relative paths.
    """
    source_root = Path(source_root)
    target_root = Path(target_root)

    synced = []
    errors = []

    for rel_path in files_to_sync:
        src = source_root / rel_path
        dst = target_root / rel_path

        try:
            # Create target directory if it doesn't exist
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            synced.append(rel_path)
        except Exception as e:
            errors.append((rel_path, str(e)))

    return synced, errors
