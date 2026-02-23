"""Module for generating text embeddings using SentenceTransformers."""

from typing import cast

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    HAS_SENTENCE_TRANSFORMERS = False


class Embedder:
    """
    Handles generation of vector embeddings for text chunks and queries.

    Uses SentenceTransformers to convert text into fixed-size numerical vectors.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedder with a specific model.

        Args:
            model_name: The name of the SentenceTransformer model to use.

        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers is not installed. Please install it with 'pip install -e .[semantic]'")
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query string.

        Args:
            text: The query text.

        Returns:
            A list of floats representing the embedding.
        """
        return cast(list[float], self.model.encode(text).tolist())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of document strings.

        Args:
            texts: A list of document texts.

        Returns:
            A list of embedding vectors.
        """
        return cast(list[list[float]], self.model.encode(texts).tolist())
