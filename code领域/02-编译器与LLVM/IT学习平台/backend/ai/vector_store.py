"""Vector Store Service - Manage document embeddings."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from .config import AISettings
from .llm import LLMService


class VectorStoreService:
    """Service for managing vector database operations."""

    def __init__(self, settings: Optional[AISettings] = None):
        self.settings = settings or AISettings()
        self._configure_vector_store()
        self.llm_service = LLMService(settings)

    def _configure_vector_store(self):
        """Configure vector store based on provider."""
        if self.settings.VECTOR_DB_PROVIDER == "chroma":
            self._configure_chroma()
        elif self.settings.VECTOR_DB_PROVIDER == "pinecone":
            self._configure_pinecone()
        else:
            raise ValueError(f"Unsupported vector store: {self.settings.VECTOR_DB_PROVIDER}")

    def _configure_chroma(self):
        """Configure ChromaDB."""
        self.client = chromadb.PersistentClient(
            path=self.settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collections = {}

    def _configure_pinecone(self):
        """Configure Pinecone (placeholder)."""
        import pinecone
        if not self.settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required for Pinecone")
        # Pinecone setup would go here
        raise NotImplementedError("Pinecone support coming soon")

    def get_or_create_collection(self, name: str) -> Any:
        """Get or create a collection."""
        if self.settings.VECTOR_DB_PROVIDER == "chroma":
            if name not in self.collections:
                self.collections[name] = self.client.get_or_create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
            return self.collections[name]
        else:
            raise NotImplementedError()

    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to vector store."""

        # Generate embeddings
        embeddings = []
        for doc in documents:
            embedding = await self.llm_service.embed(doc)
            embeddings.append(embedding)

        # Add to collection
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    async def search(
        self,
        collection_name: str,
        query: str,
        n_results: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents."""

        n_results = n_results or self.settings.TOP_K_RESULTS

        # Generate query embedding
        query_embedding = await self.llm_service.embed(query)

        # Search
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        return results

    async def add_note(
        self,
        note_id: int,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Add a note to vector store."""

        # Split content into chunks
        chunks = self._chunk_text(content)

        # Create documents and metadata
        documents = [f"{title}\n\n{chunk}" for chunk in chunks]
        metadatas = [
            {
                "note_id": note_id,
                "chunk_index": i,
                "category": category,
                "tags": tags or []
            }
            for i, chunk in enumerate(chunks)
        ]
        ids = [f"note_{note_id}_chunk_{i}" for i in range(len(chunks))]

        # Add to vector store
        await self.add_documents("notes", documents, metadatas, ids)

    async def search_notes(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for notes."""

        # Build filter
        filter_metadata = {}
        if category:
            filter_metadata["category"] = category
        if tags:
            filter_metadata["tags"] = {"$in": tags}

        # Search
        results = await self.search("notes", query, n_results, filter_metadata or None)

        # Format results
        formatted_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            formatted_results.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return formatted_results

    async def add_course_material(
        self,
        course_id: int,
        title: str,
        content: str,
        module_index: int
    ) -> None:
        """Add course material to vector store."""

        chunks = self._chunk_text(content)

        documents = [f"{title} - Module {module_index}\n\n{chunk}" for chunk in chunks]
        metadatas = [
            {
                "course_id": course_id,
                "module_index": module_index,
                "chunk_index": i,
                "type": "course_material"
            }
            for i in range(len(chunks))
        ]
        ids = [f"course_{course_id}_module_{module_index}_chunk_{i}" for i in range(len(chunks))]

        await self.add_documents("courses", documents, metadatas, ids)

    async def search_courses(
        self,
        query: str,
        course_id: Optional[int] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for course materials."""

        filter_metadata = None
        if course_id:
            filter_metadata = {"course_id": course_id}

        results = await self.search("courses", query, n_results, filter_metadata)

        formatted_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            formatted_results.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return formatted_results

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks."""

        chunk_size = self.settings.CHUNK_SIZE
        overlap = self.settings.CHUNK_OVERLAP

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at paragraph or sentence boundary
            if end < len(text):
                # Look for paragraph break
                paragraph_break = chunk.rfind("\n\n")
                if paragraph_break > chunk_size * 0.7:
                    chunk = chunk[:paragraph_break]
                    end = start + paragraph_break + 2
                else:
                    # Look for sentence break
                    sentence_break = max(
                        chunk.rfind(". "),
                        chunk.rfind("! "),
                        chunk.rfind("? ")
                    )
                    if sentence_break > chunk_size * 0.7:
                        chunk = chunk[:sentence_break + 1]
                        end = start + sentence_break + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    async def delete_document(self, collection_name: str, doc_id: str) -> None:
        """Delete a document from vector store."""

        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=[doc_id])

    async def delete_note(self, note_id: int) -> None:
        """Delete a note and all its chunks."""

        # Find all chunks for this note
        collection = self.get_or_create_collection("notes")

        # Get all documents with this note_id
        # (ChromaDB doesn't have direct filter by metadata for deletion, so we'd need to track IDs separately)
        # For now, we'll delete by pattern
        try:
            collection.delete(where={"note_id": note_id})
        except Exception as e:
            print(f"Error deleting note: {e}")

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics about a collection."""

        collection = self.get_or_create_collection(collection_name)
        count = collection.count()

        return {
            "name": collection_name,
            "document_count": count
        }

    def list_collections(self) -> List[str]:
        """List all collections."""

        return list(self.collections.keys()) if self.settings.VECTOR_DB_PROVIDER == "chroma" else []
