"""Module for the RAG (Retrieval-Augmented Generation) pipeline."""

from dotenv import load_dotenv
from llm_client import LLMClient

from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.retriever import Retriever

load_dotenv()


class RAGPipeline:
    """
    Orchestrates the retrieval and generation process to answer questions about backups.
    """

    def __init__(self) -> None:
        """
        Initialize the RAG pipeline with embedder, retriever, and LLM client.
        """
        self.embedder = Embedder()
        self.retriever = Retriever()
        # Default to groq as requested
        self.client = LLMClient(api_choice="groq")

    def answer_question(self, question: str) -> tuple[str, str]:
        """
        Answers a question using retrieved context from the backup index.

        Args:
            question: The user's question.

        Returns:
            A tuple of (answer_text, context_text).
        """
        # 1. Embed question
        query_embedding = self.embedder.embed_query(question)

        # 2. Retrieve relevant chunks
        results = self.retriever.query(query_embedding, n_results=3)

        documents = results.get("documents")
        if documents and len(documents) > 0:
            doc_list = documents[0]
            if doc_list:
                context = "\n\n".join(doc_list)
            else:
                context = ""
        else:
            context = ""

        # 3. Generate answer
        prompt = f"""
Du bist ein hilfreicher Assistent für die Suche in Backup-Strukturen.
Basierend auf den folgenden Informationen aus dem Backup-Index, beantworte die Frage des Nutzers.
Wenn die Information nicht im Kontext enthalten ist, sage dass du es nicht weißt.

Kontext:
{context}

Frage: {question}

Antwort:"""

        messages = [
            {"role": "system", "content": "Du bist ein Backup-Explorer Assistent."},
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat_completion(messages)
        return response, context
