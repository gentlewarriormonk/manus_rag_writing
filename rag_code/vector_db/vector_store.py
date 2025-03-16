"""
Vector Database and Embedding Module for RAG Writing Assistant

This module handles the conversion of text chunks to vector embeddings
and manages the vector database for similarity search.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json
import numpy as np

from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from chromadb import Client, Settings
from chromadb.config import Settings as ChromaSettings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStore:
    """
    A class for managing vector embeddings and similarity search.
    """
    
    def __init__(self, 
                 persist_directory: str = None,
                 embedding_model: str = "text-embedding-3-small",
                 collection_name: str = "user_writings"):
        """
        Initialize the VectorStore with embedding and database settings.
        
        Args:
            persist_directory: Directory to persist the vector database
            embedding_model: Name of the embedding model to use
            collection_name: Name of the collection in the vector database
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Initialize vector database
        self.db_client = self._initialize_db()
        self.collection = self._get_or_create_collection()
        
        logger.info(f"Initialized VectorStore with model={embedding_model}, collection={collection_name}")
    
    def _initialize_embeddings(self) -> Embeddings:
        """
        Initialize the embedding model.
        
        Returns:
            An initialized embedding model
        """
        try:
            # Use OpenAI embeddings by default
            embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                dimensions=1536 if self.embedding_model == "text-embedding-3-small" else None
            )
            logger.info(f"Initialized embeddings with model: {self.embedding_model}")
            return embeddings
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise
    
    def _initialize_db(self) -> Client:
        """
        Initialize the vector database client.
        
        Returns:
            An initialized database client
        """
        try:
            # Configure Chroma settings
            settings = ChromaSettings(
                anonymized_telemetry=False
            )
            
            # Create client with or without persistence
            if self.persist_directory:
                os.makedirs(self.persist_directory, exist_ok=True)
                client = Client(Settings(
                    persist_directory=self.persist_directory,
                    is_persistent=True
                ))
                logger.info(f"Initialized persistent Chroma client at: {self.persist_directory}")
            else:
                client = Client(settings)
                logger.info("Initialized in-memory Chroma client")
            
            return client
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            raise
    
    def _get_or_create_collection(self):
        """
        Get an existing collection or create a new one.
        
        Returns:
            A Chroma collection
        """
        try:
            # Check if collection exists
            existing_collections = self.db_client.list_collections()
            collection_exists = any(c.name == self.collection_name for c in existing_collections)
            
            if collection_exists:
                collection = self.db_client.get_collection(name=self.collection_name)
                logger.info(f"Retrieved existing collection: {self.collection_name}")
            else:
                collection = self.db_client.create_collection(name=self.collection_name)
                logger.info(f"Created new collection: {self.collection_name}")
            
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection: {str(e)}")
            raise
    
    def add_texts(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Add text chunks to the vector database.
        
        Args:
            chunks: List of dictionaries containing text chunks and metadata
            
        Returns:
            List of IDs for the added documents
        """
        try:
            # Extract texts, metadata, and create IDs
            texts = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [f"doc_{i}" for i in range(len(texts))]
            
            # Get embeddings for texts
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to collection {self.collection_name}")
            return ids
        except Exception as e:
            logger.error(f"Error adding texts to vector database: {str(e)}")
            raise
    
    def similarity_search(self, 
                          query: str, 
                          n_results: int = 5, 
                          filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents to the query.
        
        Args:
            query: The query text
            n_results: Number of results to return
            filter_criteria: Optional filter criteria for metadata
            
        Returns:
            List of dictionaries containing similar documents and their metadata
        """
        try:
            # Get embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_criteria
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "id": results["ids"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents for query")
            return formatted_results
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        try:
            count = self.collection.count()
            
            # Group documents by content type
            all_metadatas = self.collection.get()["metadatas"]
            content_types = {}
            
            for metadata in all_metadatas:
                content_type = metadata.get("content_type", "unknown")
                if content_type not in content_types:
                    content_types[content_type] = 0
                content_types[content_type] += 1
            
            stats = {
                "total_documents": count,
                "content_types": content_types
            }
            
            logger.info(f"Collection stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
    
    def save_to_disk(self, output_file: str) -> None:
        """
        Save the collection data to disk as JSON.
        
        Args:
            output_file: Path to save the JSON file
        """
        try:
            # Get all data from collection
            data = self.collection.get()
            
            # Format data for saving
            documents = []
            for i in range(len(data["ids"])):
                documents.append({
                    "id": data["ids"][i],
                    "text": data["documents"][i],
                    "metadata": data["metadatas"][i]
                })
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2)
            
            logger.info(f"Saved collection data to {output_file}")
        except Exception as e:
            logger.error(f"Error saving collection data: {str(e)}")
            raise
    
    def load_from_disk(self, input_file: str) -> None:
        """
        Load collection data from a JSON file.
        
        Args:
            input_file: Path to the JSON file
        """
        try:
            # Load data from file
            with open(input_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Clear existing collection
            self.collection.delete(where={})
            
            # Extract data
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            ids = [doc["id"] for doc in documents]
            
            # Get embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Loaded {len(texts)} documents from {input_file}")
        except Exception as e:
            logger.error(f"Error loading collection data: {str(e)}")
            raise


def get_embedding_model_recommendations() -> str:
    """
    Provides recommendations for embedding models.
    
    Returns:
        String containing recommendations
    """
    recommendations = """
# Embedding Model Recommendations

## OpenAI Models

1. **text-embedding-3-small** (Recommended)
   - Dimensions: 1536
   - Strengths: Excellent performance, good balance of quality and cost
   - Use case: General purpose embedding for most writing styles

2. **text-embedding-3-large**
   - Dimensions: 3072
   - Strengths: Higher quality, captures more nuanced semantic relationships
   - Use case: When highest quality retrieval is needed and cost is less of a concern

## Alternatives (If OpenAI is not preferred)

1. **Sentence Transformers**
   - Model: all-MiniLM-L6-v2
   - Dimensions: 384
   - Strengths: Open source, runs locally, no API costs
   - Limitations: Lower dimensionality, may not capture style nuances as well

2. **Cohere Embed**
   - Model: embed-english-v3.0
   - Strengths: Competitive performance with OpenAI
   - Good alternative API option

## Selection Criteria

When choosing an embedding model, consider:

1. **Quality**: How well does it capture semantic meaning and writing style?
2. **Dimensionality**: Higher dimensions can capture more information
3. **Cost**: API-based models have usage costs
4. **Speed**: Local models may be slower but have no latency
5. **Privacy**: Consider if your text contains sensitive information

## Recommendation

For this RAG-based writing assistant, we recommend:
- **Primary choice**: OpenAI's text-embedding-3-small
- **Alternative**: Sentence Transformers if local processing is preferred
"""
    return recommendations
