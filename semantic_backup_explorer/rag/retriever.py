"""Module for managing the ChromaDB vector storage and retrieval."""

from pathlib import Path
from typing import Any

try:
    import chromadb
    from chromadb.api.types import QueryResult
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    QueryResult = Any # type: ignore


class Retriever:
    """
    Manages ChromaDB vector storage for backup index chunks.

    This class handles storing and retrieving document embeddings using ChromaDB
    as the persistence layer.
    """

    def __init__(self, persist_directory: str | Path = "data/embeddings") -> None:
        """
        Initialize retriever with ChromaDB persistence.

        Args:
            persist_directory: Path to ChromaDB storage directory.
                             Will be created if it doesn't exist.

        Raises:
            ImportError: If chromadb is not installed.
        """
        if not HAS_CHROMADB:
            raise ImportError(
                "chromadb is not installed. "
                "Please install it with 'pip install -e .[semantic]'"
            )
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(name="backup_index")

    def add_chunks(self, chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        """
        Add document chunks with their embeddings to the collection.

        Args:
            chunks: List of chunk dictionaries, each containing 'content' and 'metadata'.
            embeddings: List of embedding vectors, one per chunk.

        Raises:
            ValueError: If lengths of chunks and embeddings don't match.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunk count ({len(chunks)}) must match embedding count ({len(embeddings)})")

        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [c["metadata"] for c in chunks]
        documents = [c["content"] for c in chunks]

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, query_embedding: list[float], n_results: int = 5) -> QueryResult:
        """
        Query the collection for the most relevant chunks.

        Args:
            query_embedding: The embedding vector of the query.
            n_results: Number of results to return.

        Returns:
            ChromaDB QueryResult containing documents, metadatas, and distances.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return results

    def clear(self) -> None:
        """
        Clears the collection by deleting and recreating it.
        """
        try:
            self.client.delete_collection("backup_index")
            self.collection = self.client.get_or_create_collection(name="backup_index")
        except Exception:
            pass
