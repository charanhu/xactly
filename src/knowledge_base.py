# knowledge_base.py
import os
import logging
from typing import List, Tuple
from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import config


logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages the ChromaDB vector database and PDF ingestion."""

    def __init__(self):
        """Initialize ChromaDB client and embeddings."""
        self.chroma_path = config.CHROMA_DB_PATH
        self.data_folder = config.DATA_FOLDER
        self.collection_name = config.CHROMA_COLLECTION_NAME

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        # Initialize Chroma vector store
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_path,
            create_collection_if_not_exists=True,
        )

        logger.info("Knowledge Base initialized successfully")

    def load_pdfs(self) -> List[Document]:
        """
        Load all PDFs from the data folder.

        Returns:
            List of LangChain Document objects with content and metadata
        """
        documents = []
        pdf_files = list(Path(self.data_folder).glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {self.data_folder}")
            return documents

        for pdf_file in pdf_files:
            try:
                logger.info(f"Loading PDF: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()

                # Update metadata for each page
                for i, page in enumerate(pages):
                    page.metadata.update(
                        {
                            "source": pdf_file.name,
                            "page": i + 1,
                            "file_path": str(pdf_file),
                        }
                    )
                    documents.append(page)

                logger.info(f"Loaded {len(pages)} pages from {pdf_file.name}")
            except Exception as e:
                logger.error(f"Error loading PDF {pdf_file.name}: {str(e)}")

        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into manageable chunks.

        Args:
            documents: List of LangChain Document objects

        Returns:
            List of chunked Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.KB_CHUNK_SIZE,
            chunk_overlap=config.KB_CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
        )

        chunked_docs = text_splitter.split_documents(documents)

        # Add chunk index to metadata
        for i, doc in enumerate(chunked_docs):
            doc.metadata["chunk"] = i

        logger.info(
            f"Created {len(chunked_docs)} chunks from {len(documents)} documents"
        )
        return chunked_docs

    def ingest_documents(self, documents: List[Document]) -> None:
        """
        Ingest documents into ChromaDB.

        Args:
            documents: List of LangChain Document objects to ingest
        """
        if not documents:
            logger.warning("No documents to ingest")
            return

        try:
            # Generate unique IDs for documents
            ids = [f"doc_{i}" for i in range(len(documents))]

            # Add documents to vector store
            self.vector_store.add_documents(documents=documents, ids=ids)

            logger.info(
                f"Successfully ingested {len(documents)} documents into knowledge base"
            )
        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            raise

    def initialize_knowledge_base(self) -> dict:
        """
        Initialize the knowledge base by loading and ingesting PDFs.

        Returns:
            Dictionary with initialization status
        """
        try:
            # Load PDFs
            documents = self.load_pdfs()

            if not documents:
                return {
                    "status": "warning",
                    "message": "No PDF files found in data folder",
                    "docs_loaded": 0,
                    "docs_chunked": 0,
                }

            # Chunk documents
            chunked_docs = self.chunk_documents(documents)

            # Ingest into ChromaDB
            self.ingest_documents(chunked_docs)

            return {
                "status": "success",
                "message": "Knowledge base initialized successfully",
                "docs_loaded": len(documents),
                "docs_chunked": len(chunked_docs),
                "collection_size": self.get_collection_count(),
            }
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            return {
                "status": "error",
                "message": f"Error initializing knowledge base: {str(e)}",
            }

    def search(
        self, query: str, n_results: int = None, filter: dict = None
    ) -> List[Tuple[Document, float]]:
        """
        Search the knowledge base.

        Args:
            query: Search query string
            n_results: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (Document, similarity_score) tuples
        """
        if n_results is None:
            n_results = config.KB_SEARCH_RESULTS

        try:
            # Perform similarity search with scores
            results = self.vector_store.similarity_search_with_score(
                query=query, k=n_results, filter=filter
            )

            # Convert distance to similarity score (1 - distance)
            formatted_results = [(doc, 1 - score) for doc, score in results]

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            collection_data = self.vector_store.get()
            return len(collection_data.get("ids", []))
        except Exception as e:
            logger.error(f"Error getting collection count: {str(e)}")
            return 0

    def get_collection_info(self) -> dict:
        """Get information about the current collection."""
        try:
            count = self.get_collection_count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "active",
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {"status": "error", "message": str(e)}

    def clear_knowledge_base(self) -> dict:
        """Clear the knowledge base."""
        try:
            # Delete and recreate collection
            self.vector_store.delete_collection()

            # Reinitialize vector store
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.chroma_path,
                create_collection_if_not_exists=True,
            )

            logger.info("Knowledge base cleared successfully")
            return {"status": "success", "message": "Knowledge base cleared"}
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
            return {"status": "error", "message": str(e)}

    def as_retriever(self, search_type: str = "similarity", search_kwargs: dict = None):
        """
        Get a retriever interface for the vector store.

        Args:
            search_type: Type of search ("similarity", "mmr", "similarity_score_threshold")
            search_kwargs: Additional search parameters

        Returns:
            VectorStoreRetriever object
        """
        if search_kwargs is None:
            search_kwargs = {"k": config.KB_SEARCH_RESULTS}

        return self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )
