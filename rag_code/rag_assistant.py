"""
RAG Writing Assistant - Core Integration Module

This module integrates the corpus ingestion, vector database, and language model components
to create a complete RAG-based writing assistant.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try different import strategies
try:
    from rag_code.corpus_ingestion.text_processor import TextProcessor
    from rag_code.vector_db.vector_store import VectorStore
    from rag_code.language_model.language_model import LanguageModelIntegration
    logger.info("Successfully imported from rag_code package")
except ImportError as e:
    logger.warning(f"First import attempt failed: {e}")
    try:
        # Try relative imports
        from .corpus_ingestion.text_processor import TextProcessor
        from .vector_db.vector_store import VectorStore
        from .language_model.language_model import LanguageModelIntegration
        logger.info("Successfully imported using relative imports")
    except ImportError as e2:
        logger.warning(f"Second import attempt failed: {e2}")
        try:
            # Try a more direct approach
            current_dir = Path(__file__).parent
            sys.path.insert(0, str(current_dir))
            from corpus_ingestion.text_processor import TextProcessor
            from vector_db.vector_store import VectorStore
            from language_model.language_model import LanguageModelIntegration
            logger.info("Successfully imported using direct path")
        except ImportError as e3:
            logger.error(f"All import attempts failed: {e3}")
            logger.error(f"Current directory: {os.getcwd()}")
            logger.error(f"sys.path: {sys.path}")
            raise ImportError("Could not import required modules. Please check your Python path configuration.")

class RAGWritingAssistant:
    """
    Main class that integrates all components of the RAG writing assistant.
    """
    
    def __init__(self, 
                 corpus_directory: str,
                 vector_db_directory: str,
                 embedding_model: str = "text-embedding-3-small",
                 llm_provider: str = "openai",
                 llm_model: str = "gpt-4o",
                 collection_name: str = "user_writings"):
        """
        Initialize the RAG writing assistant with all components.
        
        Args:
            corpus_directory: Directory containing the user's text files
            vector_db_directory: Directory to store the vector database
            embedding_model: Name of the embedding model to use
            llm_provider: Provider of the language model ("openai" or "anthropic")
            llm_model: Name of the language model to use
            collection_name: Name of the collection in the vector database
        """
        self.corpus_directory = corpus_directory
        self.vector_db_directory = vector_db_directory
        self.embedding_model = embedding_model
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.collection_name = collection_name
        
        # Create directories if they don't exist
        os.makedirs(corpus_directory, exist_ok=True)
        os.makedirs(vector_db_directory, exist_ok=True)
        
        # Initialize components
        self.text_processor = TextProcessor(chunk_size=750, chunk_overlap=150)
        self.vector_store = VectorStore(
            persist_directory=vector_db_directory,
            embedding_model=embedding_model,
            collection_name=collection_name
        )
        self.language_model = LanguageModelIntegration(
            model_provider=llm_provider,
            model_name=llm_model,
            temperature=0.7
        )
        
        logger.info(f"Initialized RAG Writing Assistant with corpus_directory={corpus_directory}, "
                   f"vector_db_directory={vector_db_directory}, embedding_model={embedding_model}, "
                   f"llm_provider={llm_provider}, llm_model={llm_model}")
    
    def process_corpus(self, reprocess: bool = False) -> int:
        """
        Process the corpus directory and add to vector database.
        
        Args:
            reprocess: Whether to reprocess existing files
            
        Returns:
            Number of chunks processed
        """
        try:
            # Check if we need to process the corpus
            stats = self.vector_store.get_collection_stats()
            if stats["total_documents"] > 0 and not reprocess:
                logger.info(f"Using existing vector database with {stats['total_documents']} documents")
                return stats["total_documents"]
            
            # Process the corpus
            logger.info(f"Processing corpus directory: {self.corpus_directory}")
            chunks = self.text_processor.process_directory(self.corpus_directory)
            
            # Clear existing collection if reprocessing
            if reprocess and stats["total_documents"] > 0:
                logger.info("Clearing existing vector database for reprocessing")
                self.vector_store.collection.delete(where={})
            
            # Add to vector database
            if chunks:
                logger.info(f"Adding {len(chunks)} chunks to vector database")
                self.vector_store.add_texts(chunks)
                return len(chunks)
            else:
                logger.warning(f"No text files found in {self.corpus_directory}")
                return 0
        except Exception as e:
            logger.error(f"Error processing corpus: {str(e)}")
            raise
    
    def add_file(self, file_path: str) -> int:
        """
        Process a single file and add to vector database.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Number of chunks processed
        """
        try:
            logger.info(f"Processing file: {file_path}")
            chunks = self.text_processor.process_file(file_path)
            
            if chunks:
                logger.info(f"Adding {len(chunks)} chunks to vector database")
                self.vector_store.add_texts(chunks)
                return len(chunks)
            else:
                logger.warning(f"No chunks created from {file_path}")
                return 0
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise
    
    def generate_content(self, query: str, style_adjustments: Optional[str] = None, n_results: int = 5) -> str:
        """
        Generate content based on query with optional style adjustments.
        
        Args:
            query: The user query
            style_adjustments: Optional style adjustment instructions
            n_results: Number of similar documents to retrieve
            
        Returns:
            Generated content
        """
        try:
            # Create retriever function
            def retriever(q):
                return self.vector_store.similarity_search(q, n_results=n_results)
            
            # Get context documents
            context_docs = retriever(query)
            
            if not context_docs:
                logger.warning("No relevant documents found in vector database")
                return "I don't have enough context to generate content in your style. Please add more text files to your corpus."
            
            # Generate content
            content = self.language_model.generate_with_style(query, context_docs, style_adjustments)
            
            logger.info(f"Generated content for query: {query[:50]}...")
            return content
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the corpus and vector database.
        
        Returns:
            Dictionary containing statistics
        """
        try:
            # Get vector database stats
            vector_stats = self.vector_store.get_collection_stats()
            
            # Get corpus file stats
            file_count = 0
            file_types = {}
            
            if os.path.exists(self.corpus_directory):
                files = [f for f in os.listdir(self.corpus_directory) if f.endswith('.txt')]
                file_count = len(files)
                
                for file in files:
                    # Try to determine file type from name
                    file_type = "unknown"
                    if "essay" in file.lower():
                        file_type = "essay"
                    elif "reflection" in file.lower():
                        file_type = "reflection"
                    elif "podcast" in file.lower():
                        file_type = "podcast"
                    elif "substack" in file.lower() or "newsletter" in file.lower():
                        file_type = "newsletter"
                    
                    if file_type not in file_types:
                        file_types[file_type] = 0
                    file_types[file_type] += 1
            
            stats = {
                "corpus_files": file_count,
                "file_types": file_types,
                "vector_documents": vector_stats["total_documents"],
                "content_types": vector_stats["content_types"]
            }
            
            logger.info(f"Corpus stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting corpus stats: {str(e)}")
            raise
    
    def save_state(self) -> None:
        """
        Save the current state of the vector database.
        """
        try:
            output_file = os.path.join(self.vector_db_directory, "vector_store_data.json")
            self.vector_store.save_to_disk(output_file)
            logger.info(f"Saved vector store state to {output_file}")
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")
            raise
    
    def load_state(self) -> None:
        """
        Load the saved state of the vector database.
        """
        try:
            input_file = os.path.join(self.vector_db_directory, "vector_store_data.json")
            if os.path.exists(input_file):
                self.vector_store.load_from_disk(input_file)
                logger.info(f"Loaded vector store state from {input_file}")
            else:
                logger.warning(f"No saved state found at {input_file}")
        except Exception as e:
            logger.error(f"Error loading state: {str(e)}")
            raise
