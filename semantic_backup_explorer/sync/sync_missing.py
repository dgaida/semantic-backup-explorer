import shutil
from pathlib import Path

def sync_files(files_to_sync, source_root, target_root, callback=None):
    """
    Copies files from source_root to target_root.
    files_to_sync is a list of relative paths.
    An optional callback(index, total, filename) can be provided for progress tracking.
    """
    source_root = Path(source_root)
    target_root = Path(target_root)

    synced = []
    errors = []
    total = len(files_to_sync)

    for i, rel_path in enumerate(files_to_sync):
        if callback:
            callback(i + 1, total, rel_path)

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
