import re
from pathlib import Path


def chunk_markdown(filepath):
    """
    Parses a markdown index file and splits it into chunks based on folder headers (##).
    Only folders until a depth of 4 (relative to the Root path) start a new chunk.
    Subfolders deeper than 4 are added to the chunk of their nearest depth-4 ancestor.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    root_path = None
    for line in lines:
        if line.startswith("Root: "):
            root_path = Path(line[6:].strip())
            break

    if root_path is None:
        return []

    content = "".join(lines)
    # Split by ## headers
    raw_chunks = re.split(r"\n(?=## )", content)

    chunks = []
    for rc in raw_chunks:
        rc = rc.strip()
        if not rc.startswith("## "):
            continue

        # Extract folder path from header
        lines = rc.split("\n")
        header = lines[0]
        folder_path_str = header[3:].strip()
        folder_path = Path(folder_path_str)

        try:
            relative_path = folder_path.relative_to(root_path)
            depth = len(relative_path.parts)
        except ValueError:
            # folder_path is not under root_path
            depth = 0

        if depth <= 4 or not chunks:
            chunks.append(
                {
                    "folder": str(folder_path),
                    "content": rc,
                    "metadata": {"source": str(filepath), "folder": str(folder_path), "depth": depth},
                }
            )
        else:
            # Append to last chunk
            chunks[-1]["content"] += "\n\n" + rc

    return chunks


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        chunks = chunk_markdown(sys.argv[1])
        print(json.dumps(chunks, indent=2))
