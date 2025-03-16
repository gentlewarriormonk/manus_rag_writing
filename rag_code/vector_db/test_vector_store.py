"""
Test script for the vector database and embedding module

This script tests the functionality of the VectorStore class by:
1. Loading processed text chunks
2. Creating vector embeddings
3. Testing similarity search
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
from vector_db.vector_store import VectorStore, get_embedding_model_recommendations
from corpus_ingestion.text_processor import TextProcessor
from corpus_ingestion.sample_generator import generate_sample_files

def main():
    """Test the vector database and embedding module with sample data"""
    
    # Set up paths
    sample_dir = os.path.join(project_root, "sample_data")
    db_dir = os.path.join(project_root, "vector_db_data")
    os.makedirs(db_dir, exist_ok=True)
    
    # Check if we have processed chunks, if not generate and process sample data
    chunks_file = os.path.join(sample_dir, "processed_chunks.json")
    if not os.path.exists(chunks_file):
        logger.info("No processed chunks found. Generating and processing sample data...")
        
        # Generate sample files if they don't exist
        if not os.path.exists(sample_dir) or len([f for f in os.listdir(sample_dir) if f.endswith('.txt')]) == 0:
            logger.info("Generating sample text files...")
            generate_sample_files(num_files=20)
        
        # Process the files
        processor = TextProcessor(chunk_size=750, chunk_overlap=150)
        chunks = processor.process_directory(sample_dir)
        
        # Save the processed chunks
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
        
        logger.info(f"Saved {len(chunks)} processed chunks to {chunks_file}")
    
    # Load the processed chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} processed chunks from {chunks_file}")
    
    # Initialize the vector store
    vector_store = VectorStore(
        persist_directory=db_dir,
        embedding_model="text-embedding-3-small",
        collection_name="user_writings_test"
    )
    
    # Add the chunks to the vector store
    try:
        logger.info("Adding chunks to vector store...")
        ids = vector_store.add_texts(chunks)
        logger.info(f"Added {len(ids)} chunks to vector store")
        
        # Get collection stats
        stats = vector_store.get_collection_stats()
        logger.info(f"Collection stats: {stats}")
        
        # Test similarity search
        logger.info("Testing similarity search...")
        
        # Test queries for different content types
        test_queries = [
            "What are your thoughts on AI in education?",
            "Tell me about your personal reflections on writing",
            "How do you introduce podcast episodes?",
            "What topics do you cover in your newsletter?"
        ]
        
        for query in test_queries:
            logger.info(f"Query: {query}")
            results = vector_store.similarity_search(query, n_results=2)
            
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Content type: {result['metadata']['content_type']}")
                logger.info(f"  Title: {result['metadata']['title']}")
                logger.info(f"  Text preview: {result['text'][:100]}...")
        
        # Save the collection data
        output_file = os.path.join(db_dir, "vector_store_data.json")
        vector_store.save_to_disk(output_file)
        logger.info(f"Saved vector store data to {output_file}")
        
        logger.info("Vector store test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing vector store: {str(e)}")
        logger.info("Note: This test requires OpenAI API key to be set as OPENAI_API_KEY environment variable")
        logger.info("For testing purposes, you can use a mock implementation or set up the API key")
        
        # Print embedding model recommendations
        recommendations = get_embedding_model_recommendations()
        logger.info("Embedding Model Recommendations:")
        logger.info(recommendations)

if __name__ == "__main__":
    main()
