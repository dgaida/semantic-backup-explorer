import os
import shutil
from pathlib import Path
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown
from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.retriever import Retriever
from semantic_backup_explorer.rag.rag_pipeline import RAGPipeline
from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.sync.sync_missing import sync_files

def integration_test():
    test_root = Path("tests/integration")
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True)

    backup_path = test_root / "backup_drive"
    local_path = test_root / "local_folder"

    backup_path.mkdir()
    local_path.mkdir()

    # 1. Create dummy data
    (backup_path / "old_tax").mkdir()
    (backup_path / "old_tax" / "tax_2020.pdf").write_text("tax 2020")

    (local_path / "tax_2021.pdf").write_text("tax 2021")

    # 2. Index
    print("Step 2: Indexing...")
    index_file = test_root / "index.md"
    scan_backup(backup_path, index_file)

    # 3. RAG Setup (Mocked LLM)
    print("Step 3: RAG Setup...")
    from unittest.mock import MagicMock
    import semantic_backup_explorer.rag.rag_pipeline

    original_llm = semantic_backup_explorer.rag.rag_pipeline.LLMClient
    semantic_backup_explorer.rag.rag_pipeline.LLMClient = MagicMock()
    mock_llm = semantic_backup_explorer.rag.rag_pipeline.LLMClient.return_value
    mock_llm.chat_completion.return_value = "Gefunden im Ordner old_tax."

    chunks = chunk_markdown(index_file)
    embedder = Embedder()
    retriever = Retriever(persist_directory=str(test_root / "embeddings"))
    retriever.clear()

    embeddings = embedder.embed_documents([c['content'] for c in chunks])
    retriever.add_chunks(chunks, embeddings)

    # 4. Search
    print("Step 4: Searching...")
    pipeline = RAGPipeline()
    pipeline.retriever = retriever # Override with our test retriever

    answer, context = pipeline.answer_question("Wo ist die Steuer?")
    print(f"Answer: {answer}")
    assert "old_tax" in context

    # 5. Compare
    print("Step 5: Comparing...")
    # Simulate finding the folder 'old_tax'
    backup_files = ["tax_2020.pdf"]
    diff = compare_folders(local_path, backup_files)

    print(f"Only local: {diff['only_local']}")
    assert "tax_2021.pdf" in diff["only_local"]

    # 6. Sync
    print("Step 6: Syncing...")
    synced, errors = sync_files(diff["only_local"], local_path, backup_path / "old_tax")

    print(f"Synced: {synced}")
    assert "tax_2021.pdf" in synced
    assert (backup_path / "old_tax" / "tax_2021.pdf").exists()

    print("Integration test passed!")

    # Restore
    semantic_backup_explorer.rag.rag_pipeline.LLMClient = original_llm

if __name__ == "__main__":
    try:
        integration_test()
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
