import os
from pathlib import Path

def scan_backup(root_path, output_file="data/backup_index.md"):
    """
    Recursively scans the root_path and writes every file and folder
    with its full path into a structured markdown file.
    """
    root_path = Path(root_path).resolve()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Backup Index\n\n")
        f.write(f"Root: {root_path}\n\n")

        for root, dirs, files in os.walk(root_path):
            current_path = Path(root)
            f.write(f"## {current_path}\n\n")

            for d in sorted(dirs):
                f.write(f"- {current_path / d}/\n")
            for name in sorted(files):
                f.write(f"- {current_path / name}\n")
            f.write("\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scan a backup directory and create a markdown index.")
    parser.add_argument("--path", required=True, help="Path to the backup directory to scan.")
    parser.add_argument("--output", default="data/backup_index.md", help="Path to the output markdown file.")
    args = parser.parse_args()

    scan_backup(args.path, args.output)
