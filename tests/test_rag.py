import unittest
from unittest.mock import patch

from semantic_backup_explorer.rag.embedder import Embedder

# Import pipeline AFTER patching or patch the correct path
from semantic_backup_explorer.rag.rag_pipeline import RAGPipeline


class TestRAG(unittest.TestCase):
    def test_embedder(self):
        embedder = Embedder()
        embedding = embedder.embed_query("test query")
        self.assertEqual(len(embedding), 384)  # all-MiniLM-L6-v2 dimension

    @patch("semantic_backup_explorer.rag.rag_pipeline.LLMClient")
    def test_pipeline(self, MockLLMClient):
        # Setup mock
        mock_client = MockLLMClient.return_value
        mock_client.chat_completion.return_value = "Mocked answer"

        # We also need to mock environment for Groq key if LLMClient still complains
        # but since we patched the class, it shouldn't.

        pipeline = RAGPipeline()
        # Add some mock data to retriever
        chunks = [
            {"folder": "/path/to/tax", "content": "## /path/to/tax\n- tax_2021.pdf", "metadata": {"folder": "/path/to/tax"}}
        ]
        embeddings = pipeline.embedder.embed_documents([c["content"] for c in chunks])
        pipeline.retriever.clear()
        pipeline.retriever.add_chunks(chunks, embeddings)

        answer, context = pipeline.answer_question("Wo sind die Steuerunterlagen?")

        self.assertEqual(answer, "Mocked answer")
        self.assertIn("/path/to/tax", context)
        mock_client.chat_completion.assert_called()


if __name__ == "__main__":
    unittest.main()
