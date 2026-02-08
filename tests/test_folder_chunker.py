import pytest
from pathlib import Path
from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown
from semantic_backup_explorer.indexer.scan_backup import scan_backup
import shutil
import os

def test_chunk_markdown_depth(tmp_path):
    test_root = tmp_path / "test_backup"
    test_root.mkdir()

    # Create depth 6 structure
    (test_root / "d1" / "d2" / "d3" / "d4" / "d5" / "d6").mkdir(parents=True)
    (test_root / "d1" / "d2" / "d3" / "d4" / "file4.txt").touch()
    (test_root / "d1" / "d2" / "d3" / "d4" / "d5" / "file5.txt").touch()

    index_file = tmp_path / "test_index.md"
    scan_backup(str(test_root), str(index_file))

    chunks = chunk_markdown(str(index_file))

    # Root (0), d1 (1), d2 (2), d3 (3), d4 (4) = 5 chunks
    assert len(chunks) == 5

    # Find the chunk for d4
    d4_chunk = next(c for c in chunks if "d4" in c["folder"] and "d5" not in c["folder"])
    assert d4_chunk["metadata"]["depth"] == 4

    # d5 and d6 should be in d4_chunk
    assert "##" in d4_chunk["content"]
    assert str(test_root / "d1" / "d2" / "d3" / "d4") in d4_chunk["content"]
    assert str(test_root / "d1" / "d2" / "d3" / "d4" / "d5") in d4_chunk["content"]
    assert str(test_root / "d1" / "d2" / "d3" / "d4" / "d5" / "d6") in d4_chunk["content"]

def test_chunk_markdown_multiple_branches(tmp_path):
    test_root = tmp_path / "test_backup"
    test_root.mkdir()

    (test_root / "branch1" / "sub").mkdir(parents=True)
    (test_root / "branch2" / "sub").mkdir(parents=True)

    index_file = tmp_path / "test_index.md"
    scan_backup(str(test_root), str(index_file))

    chunks = chunk_markdown(str(index_file))

    # Root (0), branch1 (1), branch1/sub (2), branch2 (1), branch2/sub (2) = 5 chunks
    assert len(chunks) == 5
