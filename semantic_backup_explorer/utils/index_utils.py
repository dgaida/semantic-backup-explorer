import os


def normalize_path(path):
    """Normalizes path to use forward slashes for internal comparison."""
    if not path:
        return ""
    return path.replace("\\", "/").rstrip("/")


def find_backup_folder(folder_name, index_path):
    """
    Searches the index file for a folder header (##) that contains folder_name.
    Returns the first matching full path found.
    Handles partial matches like 'Finanzen' matching 'Finanzen (Backup)'.
    """
    if not os.path.exists(index_path):
        return None

    # folder_name might also contain backslashes if passed from a Windows path
    clean_folder_name = folder_name.replace("\\", "/").rstrip("/").split("/")[-1].lower()

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                header_path = line[3:].strip()
                norm_header = header_path.replace("\\", "/").rstrip("/")
                header_folder_name = norm_header.split("/")[-1].lower()

                # Exact match or partial match (e.g. "Finanzen" in "Finanzen (Backup)")
                if clean_folder_name == header_folder_name or clean_folder_name in header_folder_name:
                    return header_path
    return None


def get_all_files_from_index(backup_root, index_path):
    """
    Extracts all file paths from the index that are sub-paths of backup_root.
    Returns a list of relative paths.
    """
    files = []
    if not os.path.exists(index_path):
        return files

    norm_root = normalize_path(backup_root)

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("- "):
                file_path = line[2:].strip()
                # Skip directories (which end in / or \ in our index format)
                if file_path.endswith("/") or file_path.endswith("\\"):
                    continue

                norm_file = file_path.replace("\\", "/")

                if norm_file.startswith(norm_root):
                    # Check if it's actually a subpath (not just a prefix match of a sibling folder)
                    remainder = norm_file[len(norm_root) :]
                    if not remainder or remainder.startswith("/"):
                        rel_path = remainder.lstrip("/")
                        if rel_path:
                            # Use current OS separator for the returned relative paths
                            # so they match what os.walk produces in compare_folders
                            files.append(rel_path.replace("/", os.sep))
    return files
