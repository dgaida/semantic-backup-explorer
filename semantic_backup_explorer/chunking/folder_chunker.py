import re
from pathlib import Path

def chunk_markdown(filepath):
    """
    Parses a markdown index file and splits it into chunks based on folder headers (##).
    Each chunk contains the folder path and the list of files/subfolders it contains.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by ## headers
    raw_chunks = re.split(r'\n(?=## )', content)

    chunks = []
    for rc in raw_chunks:
        rc = rc.strip()
        if not rc.startswith('## '):
            continue

        # Extract folder path from header
        lines = rc.split('\n')
        header = lines[0]
        folder_path = header[3:].strip()

        chunks.append({
            "folder": str(folder_path),
            "content": rc,
            "metadata": {
                "source": str(filepath),
                "folder": str(folder_path)
            }
        })

    return chunks

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        chunks = chunk_markdown(sys.argv[1])
        print(json.dumps(chunks, indent=2))
