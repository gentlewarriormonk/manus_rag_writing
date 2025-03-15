"""
Test script for the language model integration module

This script tests the functionality of the LanguageModelIntegration class by:
1. Loading processed text chunks
2. Setting up a mock retriever function
3. Testing content generation with style adjustments
"""

import os
import sys
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import the modules
sys.path.append(os.path.join(project_root, "code"))
from language_model.language_model import LanguageModelIntegration, get_language_model_recommendations
from vector_db.vector_store import VectorStore

def mock_retriever(query):
    """
    Mock retriever function that returns sample documents.
    Used when actual vector store is not available.
    """
    # Sample documents that would normally come from vector store
    sample_docs = [
        {
            "text": "The intersection of artificial intelligence and education represents one of the most promising frontiers in modern learning. As we stand at this technological crossroads, it's crucial to consider not just the efficiency gains but the fundamental transformation of how knowledge is transmitted and internalized.",
            "metadata": {
                "title": "The Future of Learning in an AI-Driven World",
                "content_type": "essay",
                "tags": ["education", "technology", "future"]
            }
        },
        {
            "text": "I find myself increasingly drawn to the liminal spaces between disciplines. The most interesting questions seem to emerge not from the center of established fields but from their overlapping boundaries. This intellectual borderland requires a certain comfort with ambiguity, a willingness to speak multiple academic languages imperfectly rather than a single one fluently.",
            "metadata": {
                "title": "Thoughts on Interdisciplinary Approaches",
                "content_type": "reflection",
                "tags": ["personal", "growth", "learning"]
            }
        }
    ]
    
    logger.info(f"Mock retriever called with query: {query}")
    return sample_docs

def main():
    """Test the language model integration module"""
    
    # Set up paths
    sample_dir = os.path.join(project_root, "sample_data")
    db_dir = os.path.join(project_root, "vector_db_data")
    
    # Check if we have processed chunks for real retrieval
    chunks_file = os.path.join(sample_dir, "processed_chunks.json")
    vector_store_file = os.path.join(db_dir, "vector_store_data.json")
    
    # Try to set up real retriever if data exists
    retriever = mock_retriever
    if os.path.exists(chunks_file) and os.path.exists(db_dir):
        try:
            logger.info("Attempting to set up real vector store retriever...")
            
            # Initialize vector store
            vector_store = VectorStore(
                persist_directory=db_dir,
                embedding_model="text-embedding-3-small",
                collection_name="user_writings_test"
            )
            
            # If vector store data exists, load it
            if os.path.exists(vector_store_file):
                vector_store.load_from_disk(vector_store_file)
                
                # Create real retriever function
                def real_retriever(query):
                    return vector_store.similarity_search(query, n_results=3)
                
                retriever = real_retriever
                logger.info("Using real vector store retriever")
            else:
                logger.info("Vector store data not found, using mock retriever")
        except Exception as e:
            logger.warning(f"Error setting up real retriever: {str(e)}")
            logger.info("Falling back to mock retriever")
    
    # Initialize the language model integration
    try:
        logger.info("Initializing language model integration...")
        
        # Try OpenAI first
        try:
            lm_integration = LanguageModelIntegration(
                model_provider="openai",
                model_name="gpt-4o",
                temperature=0.7
            )
            logger.info("Successfully initialized OpenAI language model")
        except Exception as e:
            logger.warning(f"Error initializing OpenAI model: {str(e)}")
            logger.info("Trying Anthropic model instead...")
            
            # Fall back to Anthropic if OpenAI fails
            try:
                lm_integration = LanguageModelIntegration(
                    model_provider="anthropic",
                    model_name="claude-3-sonnet-20240229",
                    temperature=0.7
                )
                logger.info("Successfully initialized Anthropic language model")
            except Exception as e:
                logger.error(f"Error initializing Anthropic model: {str(e)}")
                logger.info("Note: This test requires either OpenAI or Anthropic API key to be set")
                
                # Print language model recommendations
                recommendations = get_language_model_recommendations()
                logger.info("Language Model Recommendations:")
                logger.info(recommendations)
                return
        
        # Test queries with different style adjustments
        test_queries = [
            "Write a short paragraph about the future of education",
            "Write a reflection on the creative process [make this more philosophical]",
            "Draft an introduction for a podcast about technology trends [make this more conversational]",
            "Write a newsletter update about recent developments in AI [make this more technical]"
        ]
        
        for query in test_queries:
            logger.info(f"\nTesting query: {query}")
            
            # Get context documents
            context_docs = retriever(query)
            
            # Generate content
            content = lm_integration.generate_with_style(query, context_docs)
            
            logger.info(f"Generated content:\n{content[:300]}...\n")
        
        logger.info("Language model integration test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing language model integration: {str(e)}")
        logger.info("Note: This test requires API keys to be set as environment variables")
        
        # Print language model recommendations
        recommendations = get_language_model_recommendations()
        logger.info("Language Model Recommendations:")
        logger.info(recommendations)

if __name__ == "__main__":
    main()
