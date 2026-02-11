"""Tests for core backup operations."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semantic_backup_explorer.core.backup_operations import BackupOperations


class TestBackupOperations:
    @pytest.fixture
    def mock_rag_pipeline(self):
        return MagicMock()

    @pytest.fixture
    def index_path(self, tmp_path):
        index_file = tmp_path / "backup_index.md"
        index_file.write_text("# Backup Index\n\n## /backup/photos\n- /backup/photos/img1.jpg\n")
        return index_file

    def test_find_and_compare_local_not_exists(self, index_path):
        ops = BackupOperations(index_path=index_path)
        result = ops.find_and_compare(Path("/non/existent/path"))
        assert result.error is not None
        assert "does not exist" in result.error

    @patch("semantic_backup_explorer.core.backup_operations.find_backup_folder")
    @patch("semantic_backup_explorer.core.backup_operations.get_all_files_from_index")
    @patch("semantic_backup_explorer.core.backup_operations.compare_folders")
    def test_find_and_compare_success(self, mock_compare, mock_get_files, mock_find_folder, index_path, tmp_path):
        local_path = tmp_path / "photos"
        local_path.mkdir()

        mock_find_folder.return_value = "/backup/photos"
        mock_get_files.return_value = {"img1.jpg": 1234.5}
        mock_compare.return_value = {"only_local": ["img2.jpg"], "only_backup": [], "in_both": ["img1.jpg"]}

        ops = BackupOperations(index_path=index_path)
        result = ops.find_and_compare(local_path)

        assert result.backup_path == Path("/backup/photos")
        assert result.only_local == ["img2.jpg"]
        assert result.in_both == ["img1.jpg"]
        assert result.error is None

    @patch("semantic_backup_explorer.core.backup_operations.find_backup_folder")
    def test_find_and_compare_no_match_no_rag(self, mock_find_folder, index_path, tmp_path):
        local_path = tmp_path / "unknown"
        local_path.mkdir()
        mock_find_folder.return_value = None

        ops = BackupOperations(index_path=index_path)
        result = ops.find_and_compare(local_path)

        assert result.backup_path is None
        assert "No matching backup folder found" in result.error

    @patch("semantic_backup_explorer.core.backup_operations.find_backup_folder")
    def test_find_and_compare_rag_fallback(self, mock_find_folder, mock_rag_pipeline, index_path, tmp_path):
        local_path = tmp_path / "photos"
        local_path.mkdir()
        mock_find_folder.return_value = None
        mock_rag_pipeline.answer_question.return_value = ("/backup/photos_from_rag", "context")

        with patch.object(BackupOperations, "_rag_search", return_value="/backup/photos_from_rag"):
            with patch("semantic_backup_explorer.core.backup_operations.get_all_files_from_index", return_value={}):
                with patch(
                    "semantic_backup_explorer.core.backup_operations.compare_folders",
                    return_value={"only_local": [], "only_backup": [], "in_both": []},
                ):
                    ops = BackupOperations(index_path=index_path, rag_pipeline=mock_rag_pipeline)
                    result = ops.find_and_compare(local_path)

                    assert result.backup_path == Path("/backup/photos_from_rag")
                    assert result.error is None
