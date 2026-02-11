"""Module for scanning backup directories and creating a markdown index."""

import os
import subprocess
from pathlib import Path
from typing import Callable, Optional

from tqdm import tqdm


def get_volume_label(path: str | Path) -> Optional[str]:
    """
    Attempts to get the volume label of the drive containing the path on Windows.

    Args:
        path: Path on the drive.

    Returns:
        The volume label string, or None if not on Windows or if detection fails.
    """
    if os.name != "nt":
        return None

    try:
        abs_path = os.path.abspath(path)
        drive = os.path.splitdrive(abs_path)[0]
        if not drive:
            return None

        # Command: wmic logicaldisk where name="C:" get volumename
        output = subprocess.check_output(
            f'wmic logicaldisk where name="{drive}" get volumename', shell=True, stderr=subprocess.STDOUT
        ).decode("utf-8", errors="ignore")

        lines = [line.strip() for line in output.split("\n") if line.strip()]
        # Expected output:
        # VolumeName
        # MyBackup
        if len(lines) > 1 and lines[0].lower().startswith("volumename"):
            return lines[1]
    except Exception:
        pass
    return None


def scan_backup(
    root_path: str | Path,
    output_file: str | Path = "data/backup_index.md",
    callback: Optional[Callable[[int, str], None]] = None,
) -> None:
    """
    Recursively scans the root_path and writes every file and folder
    with its full path into a structured markdown file.

    Args:
        root_path: Path to the backup directory to scan.
        output_file: Path to the output markdown file.
        callback: Optional callback function called with (count, current_root).

    Raises:
        FileNotFoundError: If root_path does not exist.
        NotADirectoryError: If root_path is not a directory.
        PermissionError: If output_file cannot be written.
    """
    root_path = Path(root_path).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Backup path does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Backup path is not a directory: {root_path}")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        label = get_volume_label(root_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Backup Index\n\n")
            root_line = f"Root: {root_path}"
            if label:
                root_line += f" (Label: {label})"
            f.write(f"{root_line}\n\n")

            count = 0
            for root, dirs, files in tqdm(os.walk(root_path), desc="Scanning directories"):
                count += 1
                if callback:
                    callback(count, root)
                current_path = Path(root)
                f.write(f"## {current_path}\n\n")

                for d in sorted(dirs):
                    f.write(f"- {current_path / d}/\n")
                for name in sorted(files):
                    file_path = current_path / name
                    try:
                        mtime = os.path.getmtime(file_path)
                        f.write(f"- {file_path} | mtime:{mtime}\n")
                    except Exception:
                        f.write(f"- {file_path}\n")
                f.write("\n")
    except PermissionError as e:
        raise PermissionError(f"Cannot write to output file: {output_path}") from e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scan a backup directory and create a markdown index.")
    parser.add_argument("--path", required=True, help="Path to the backup directory to scan.")
    parser.add_argument("--output", default="data/backup_index.md", help="Path to the output markdown file.")
    args = parser.parse_args()

    try:
        scan_backup(args.path, args.output)
    except Exception as e:
        print(f"Error: {e}")
