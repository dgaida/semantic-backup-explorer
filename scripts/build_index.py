import argparse
import os
from pathlib import Path
from tqdm import tqdm
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown
from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.retriever import Retriever

def main():
    parser = argparse.ArgumentParser(description="Build semantic backup index.")
    parser.add_argument("--path", required=True, help="Path to backup drive/folder.")
    parser.add_argument("--output", default="data/backup_index.md", help="Path to output markdown index.")
    args = parser.parse_args()

    # 1. Scan
    print(f"Scanning {args.path}...")
    scan_backup(args.path, args.output)

    # 2. Chunk
    print("Chunking index...")
    chunks = chunk_markdown(args.output)
    print(f"Created {len(chunks)} chunks.")

    # 3. Embed and Store
    print("Initializing embedder and retriever...")
    embedder = Embedder()
    retriever = Retriever()
    retriever.clear()

    print("Generating embeddings and storing in ChromaDB...")
    texts = [c['content'] for c in chunks]

    # Process in batches if many
    batch_size = 32
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i+batch_size]
        batch_chunks = chunks[i:i+batch_size]
        batch_embeddings = embedder.embed_documents(batch_texts)
        retriever.add_chunks(batch_chunks, batch_embeddings)

    print("Indexing complete!")

if __name__ == "__main__":
    main()
