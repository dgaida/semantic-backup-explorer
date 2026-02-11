"""Module for chunking the markdown index into folder-based sections."""

import re
from pathlib import Path
from typing import Any


def chunk_markdown(filepath: str | Path) -> list[dict[str, Any]]:
    """
    Parses a markdown index file and splits it into chunks based on folder headers (##).

    Only folders until a depth of 4 (relative to the Root path) start a new chunk.
    Subfolders deeper than 4 are added to the chunk of their nearest depth-4 ancestor.

    Args:
        filepath: Path to the markdown index file.

    Returns:
        A list of chunk dictionaries, each containing 'folder', 'content', and 'metadata'.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    root_path = None
    drive_label = None
    for line in lines:
        if line.startswith("Root: "):
            content_after_root = line[6:].strip()
            # Handle "Root: J:\ (Label: MyBackup)"
            if " (Label: " in content_after_root:
                root_part, label_part = content_after_root.split(" (Label: ", 1)
                root_path = Path(root_part.strip())
                drive_label = label_part.rstrip(")").strip()
            else:
                root_path = Path(content_after_root)
            break

    if root_path is None:
        return []

    content = "".join(lines)
    # Split by ## headers
    raw_chunks = re.split(r"\n(?=## )", content)

    chunks: list[dict[str, Any]] = []
    for rc in raw_chunks:
        rc = rc.strip()
        if not rc.startswith("## "):
            continue

        # Extract folder path from header
        rc_lines = rc.split("\n")
        header = rc_lines[0]
        folder_path_str = header[3:].strip()
        folder_path = Path(folder_path_str)

        try:
            relative_path = folder_path.relative_to(root_path)
            depth = len(relative_path.parts)
        except ValueError:
            # folder_path is not under root_path
            depth = 0

        chunk_content = rc
        if drive_label:
            chunk_content = f"Backup Drive: {drive_label}\n{chunk_content}"

        if depth <= 4 or not chunks:
            chunks.append(
                {
                    "folder": str(folder_path),
                    "content": chunk_content,
                    "metadata": {"source": str(filepath), "folder": str(folder_path), "depth": depth},
                }
            )
        else:
            # Append to last chunk
            current_content = str(chunks[-1]["content"])
            chunks[-1]["content"] = current_content + "\n\n" + chunk_content

    return chunks


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        chunks = chunk_markdown(sys.argv[1])
        print(json.dumps(chunks, indent=2))
