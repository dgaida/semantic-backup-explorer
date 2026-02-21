"""Core business logic for backup operations."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from semantic_backup_explorer.compare.folder_diff import FolderDiffResult, compare_folders
from semantic_backup_explorer.rag.rag_pipeline import RAGPipeline
from semantic_backup_explorer.utils.index_utils import find_backup_folder, get_all_files_from_index

logger = logging.getLogger(__name__)


@dataclass
class BackupComparisonResult:
    """Result of comparing a local folder with its backup."""

    local_path: Path
    backup_path: Optional[Path]
    only_local: list[str]
    only_backup: list[str]
    in_both: list[str]
    error: Optional[str] = None


class BackupOperations:
    """High-level operations for backup management."""

    def __init__(self, index_path: Path, rag_pipeline: Optional[RAGPipeline] = None):
        """
        Initialize BackupOperations.

        Args:
            index_path: Path to the backup index file.
            rag_pipeline: Optional RAG pipeline for semantic folder matching.
        """
        self.index_path = index_path
        self.rag_pipeline = rag_pipeline

    def find_and_compare(self, local_path: Path) -> BackupComparisonResult:
        """
        Finds the matching backup folder and compares contents.

        Args:
            local_path: The local folder to compare.

        Returns:
            A BackupComparisonResult object.
        """
        if not local_path.exists():
            return BackupComparisonResult(
                local_path=local_path,
                backup_path=None,
                only_local=[],
                only_backup=[],
                in_both=[],
                error=f"Local path does not exist: {local_path}",
            )

        folder_name = local_path.name or str(local_path)
        backup_folder_str = find_backup_folder(folder_name, self.index_path)

        # Fallback to RAG if enabled and no direct match found
        if not backup_folder_str and self.rag_pipeline is not None:
            logger.info(f"No direct match for {folder_name}, trying RAG search...")
            backup_folder_str = self._rag_search(folder_name)

        if not backup_folder_str:
            return BackupComparisonResult(
                local_path=local_path,
                backup_path=None,
                only_local=[],  # Could potentially list all local files here
                only_backup=[],
                in_both=[],
                error=f"No matching backup folder found for {folder_name}",
            )

        backup_path = Path(backup_folder_str)
        backup_files = get_all_files_from_index(backup_folder_str, self.index_path)
        diff: FolderDiffResult = compare_folders(local_path, backup_files)

        return BackupComparisonResult(
            local_path=local_path,
            backup_path=backup_path,
            only_local=diff["only_local"],
            only_backup=diff["only_backup"],
            in_both=diff["in_both"],
        )

    def _rag_search(self, folder_name: str) -> Optional[str]:
        """
        Search for a folder using the RAG pipeline.

        Args:
            folder_name: The folder name to search for.

        Returns:
            The path of the most likely matching folder, or None.
        """
        if not self.rag_pipeline:
            return None

        try:
            # We ask the RAG pipeline specifically for the path
            question = f"In welchem Ordner im Backup befinden sich die Dateien für '{folder_name}'? Nenne nur den Pfad."
            answer, _ = self.rag_pipeline.answer_question(question)

            # Simple extraction from answer
            potential_path = answer.strip().split("\n")[0].strip()
            if potential_path.startswith("## "):
                potential_path = potential_path[3:]

            if "/" in potential_path or "\\" in potential_path:
                return potential_path
        except Exception as e:
            logger.error(f"Error during RAG search for folder: {e}")

        return None
