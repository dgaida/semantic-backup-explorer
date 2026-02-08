import chromadb


class Retriever:
    def __init__(self, persist_directory="data/embeddings"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="backup_index")

    def add_chunks(self, chunks, embeddings):
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [c["metadata"] for c in chunks]
        documents = [c["content"] for c in chunks]

        self.collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_embedding, n_results=5):
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return results

    def clear(self):
        try:
            self.client.delete_collection("backup_index")
            self.collection = self.client.get_or_create_collection(name="backup_index")
        except Exception:
            pass
