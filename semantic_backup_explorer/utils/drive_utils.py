"""Utilities for drive and volume information."""

import os
import subprocess
from pathlib import Path
from typing import Optional


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
