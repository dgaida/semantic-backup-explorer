# Architecture

This document describes the high-level architecture of the Semantic Backup Explorer.

## Overview

The project is a RAG (Retrieval-Augmented Generation) based system designed to help users search through their file backups and synchronize local changes.

## Components

### 1. Library (`semantic_backup_explorer/`)

- **`core/`**: Contains the main business logic (`BackupOperations`). It orchestrates folder finding and comparison.
- **`rag/`**: Implements the RAG pipeline using `SentenceTransformers` for embeddings and `ChromaDB` for vector storage. It uses `llm_client` to interface with Groq.
- **`indexer/`**: Handles the recursive scanning of backup directories and produces a Markdown index file.
- **`chunking/`**: Partitions the Markdown index into folder-based chunks suitable for the vector database.
- **`compare/`**: Logic for comparing local directory contents with the backup index, considering both existence and modification times.
- **`sync/`**: Handles the actual copying of files from source to destination.
- **`utils/`**: Shared utilities for configuration, logging, path normalization, and compatibility.

### 2. CLI & UI (`semantic_backup_explorer/cli/`)

- **`ui/gradio_app.py`**: A web interface built with Gradio for an interactive experience.
- **`commands/`**: (Future) Place for modular CLI commands.

### 3. Scripts (`scripts/`)

Standalone Python scripts for common tasks:
- `auto_sync.py`: Automated synchronization based on a config file.
- `build_index.py`: Scans a backup drive and builds the vector database.

## Data Flow

1. **Scanning**: `indexer` scans the backup drive -> `backup_index.md`.
2. **Indexing**: `chunking` reads `backup_index.md` -> `rag.Embedder` creates vectors -> `rag.Retriever` stores in `ChromaDB`.
3. **Search**: User query -> `rag.Embedder` -> `rag.Retriever` (context) -> `llm_client` (Groq) -> Answer.
4. **Compare & Sync**: Local folder -> `core.BackupOperations` finds backup counterpart (keyword or RAG) -> `compare` identifies differences -> `sync` copies files.
