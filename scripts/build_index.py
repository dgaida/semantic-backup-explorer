"""Script for building the semantic backup index and generating embeddings."""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm

from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.retriever import Retriever
from semantic_backup_explorer.utils.compatibility import check_python_version
from semantic_backup_explorer.utils.config import BackupConfig
from semantic_backup_explorer.utils.logging_utils import setup_logging

check_python_version()


def main() -> None:
    """Main entry point for the build_index script."""
    parser = argparse.ArgumentParser(description="Build semantic backup index.")
    parser.add_argument("--path", help="Path to backup drive/folder (overrides config).")
    parser.add_argument("--output", help="Path to output markdown index (overrides config).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)

    # Load Config
    config = BackupConfig()
    if args.path:
        config.backup_drive = Path(args.path)
    if args.output:
        config.index_path = Path(args.output)

    # 1. Scan
    logger.info(f"Scanning {config.backup_drive}...")
    try:
        scan_backup(config.backup_drive, config.index_path)
    except Exception as e:
        logger.error(f"Scanning failed: {e}")
        sys.exit(1)

    # 2. Chunk
    logger.info("Chunking index...")
    chunks = chunk_markdown(config.index_path)
    logger.info(f"Created {len(chunks)} chunks.")

    # 3. Embed and Store
    logger.info("Initializing embedder and retriever...")
    embedder = Embedder()
    retriever = Retriever(persist_directory=config.embeddings_path)
    retriever.clear()

    logger.info("Generating embeddings and storing in ChromaDB...")
    texts = [c["content"] for c in chunks]

    # Process in batches if many
    batch_size = 32
    for i in tqdm(range(0, len(texts), batch_size), desc="Building vector DB"):
        batch_texts = texts[i : i + batch_size]
        batch_chunks = chunks[i : i + batch_size]
        batch_embeddings = embedder.embed_documents(batch_texts)
        retriever.add_chunks(batch_chunks, batch_embeddings)

    logger.info("Indexing complete!")


if __name__ == "__main__":
    main()
