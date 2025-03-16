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

# First log the current environment to help with debugging
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Current file: {__file__}")
logger.info(f"sys.path: {sys.path}")

# Improve path handling for robust imports
current_file = Path(__file__).resolve()
module_dir = current_file.parent  # rag_code directory
project_root = module_dir.parent   # Project root

# Add key directories to path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.info(f"Added project root to sys.path: {project_root}")

if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
    logger.info(f"Added module directory to sys.path: {module_dir}")

# Try different import strategies with improved error handling
try:
    # Try absolute imports first
    from rag_code.corpus_ingestion.text_processor import TextProcessor
    from rag_code.vector_db.vector_store import VectorStore
    from rag_code.language_model.language_model import LanguageModelIntegration
    logger.info("Successfully imported using absolute imports from rag_code package")
except ImportError as e:
    logger.warning(f"Absolute imports failed: {e}")
    try:
        # Try relative imports
        from .corpus_ingestion.text_processor import TextProcessor
        from .vector_db.vector_store import VectorStore
        from .language_model.language_model import LanguageModelIntegration
        logger.info("Successfully imported using relative imports")
    except ImportError as e2:
        logger.warning(f"Relative imports failed: {e2}")
        try:
            # Try a more direct approach with improved path handling
            corpus_ingestion_path = module_dir / "corpus_ingestion"
            vector_db_path = module_dir / "vector_db"
            language_model_path = module_dir / "language_model"
            
            if corpus_ingestion_path.exists() and vector_db_path.exists() and language_model_path.exists():
                logger.info(f"Found required subdirectories in {module_dir}")
                
                sys.path.insert(0, str(corpus_ingestion_path))
                sys.path.insert(0, str(vector_db_path))
                sys.path.insert(0, str(language_model_path))
                
                from text_processor import TextProcessor
                from vector_store import VectorStore
                from language_model import LanguageModelIntegration
                logger.info("Successfully imported using direct path")
            else:
                logger.error(f"Required subdirectories not found in {module_dir}")
                logger.error(f"corpus_ingestion exists: {corpus_ingestion_path.exists()}")
                logger.error(f"vector_db exists: {vector_db_path.exists()}")
                logger.error(f"language_model exists: {language_model_path.exists()}")
                raise ImportError("Required module directories not found")
        except ImportError as e3:
            logger.error(f"All import attempts failed: {e3}")
            logger.error(f"Current directory: {os.getcwd()}")
            logger.error(f"Module directory contents: {[x.name for x in module_dir.iterdir()] if module_dir.exists() else 'directory not found'}")
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
        logger.info("Initializing TextProcessor...")
        self.text_processor = TextProcessor(chunk_size=750, chunk_overlap=150)
        
        logger.info("Initializing VectorStore...")
        self.vector_store = VectorStore(
            persist_directory=vector_db_directory,
            embedding_model=embedding_model,
            collection_name=collection_name
        )
        
        logger.info("Initializing LanguageModelIntegration...")
        self.language_model = LanguageModelIntegration(
            model_provider=llm_provider,
            model_name=llm_model,
            temperature=0.7
        )
        
        logger.info(f"Initialized RAG Writing Assistant with corpus_directory={corpus_directory}, "
                   f"vector_db_directory={vector_db_directory}, embedding_model={embedding_model}, "
                   f"llm_provider={llm_provider}, llm_model={llm_model}")
    
    # Rest of the class implementation remains the same
    # ...
