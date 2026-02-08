from dotenv import load_dotenv
from llm_client import LLMClient

from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.retriever import Retriever

load_dotenv()


class RAGPipeline:
    def __init__(self):
        self.embedder = Embedder()
        self.retriever = Retriever()
        # Default to groq as requested
        self.client = LLMClient(api_choice="groq")

    def answer_question(self, question):
        # 1. Embed question
        query_embedding = self.embedder.embed_query(question)

        # 2. Retrieve relevant chunks
        results = self.retriever.query(query_embedding, n_results=3)

        context = "\n\n".join(results["documents"][0])

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
