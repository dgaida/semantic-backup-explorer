"""Module for generating text embeddings using SentenceTransformers."""

from sentence_transformers import SentenceTransformer


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
        """
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query string.

        Args:
            text: The query text.

        Returns:
            A list of floats representing the embedding.
        """
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of document strings.

        Args:
            texts: A list of document texts.

        Returns:
            A list of embedding vectors.
        """
        return self.model.encode(texts).tolist()  # type: ignore[no-any-return]
