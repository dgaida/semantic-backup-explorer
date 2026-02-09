import inspect
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

    # Check callback signature for backwards compatibility
    callback_args = 0
    if callback:
        try:
            callback_args = len(inspect.signature(callback).parameters)
        except Exception:
            # Fallback for callbacks that don't support signature inspection
            callback_args = 3

    for i, rel_path in enumerate(files_to_sync):
        src = source_root / rel_path
        dst = target_root / rel_path

        error_msg = None
        try:
            # Create target directory if it doesn't exist
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            synced.append(rel_path)
        except Exception as e:
            error_msg = str(e)
            errors.append((rel_path, error_msg))

        if callback:
            if callback_args >= 4:
                callback(i + 1, total, rel_path, error_msg)
            else:
                callback(i + 1, total, rel_path)

    return synced, errors
