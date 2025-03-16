"""
Test script for the corpus ingestion module

This script tests the functionality of the TextProcessor class by:
1. Generating sample text files
2. Processing those files
3. Displaying the resulting chunks and metadata
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import the modules directly
sys.path.append(os.path.join(project_root, "code"))
from corpus_ingestion.text_processor import TextProcessor, get_file_organization_recommendations
from corpus_ingestion.sample_generator import generate_sample_files

def main():
    """Test the corpus ingestion module with sample data"""
    
    sample_dir = os.path.join(project_root, "sample_data")
    
    # Generate sample files if they don't exist
    if not os.path.exists(sample_dir) or len(os.listdir(sample_dir)) == 0:
        print("Generating sample text files...")
        generate_sample_files(num_files=20)
    else:
        print(f"Using existing sample files in {sample_dir}")
    
    # Initialize the text processor
    processor = TextProcessor(chunk_size=750, chunk_overlap=150)
    
    # Process all files in the sample directory
    print("\nProcessing text files...")
    chunks = processor.process_directory(sample_dir)
    
    # Display summary of processed chunks
    print(f"\nProcessed {len(chunks)} chunks from the sample files")
    
    # Group chunks by content type
    content_types = {}
    for chunk in chunks:
        content_type = chunk['metadata']['content_type']
        if content_type not in content_types:
            content_types[content_type] = 0
        content_types[content_type] += 1
    
    print("\nChunks by content type:")
    for content_type, count in content_types.items():
        print(f"  - {content_type}: {count} chunks")
    
    # Display a sample chunk with its metadata
    if chunks:
        print("\nSample chunk with metadata:")
        sample_chunk = chunks[0]
        print(f"Metadata: {json.dumps(sample_chunk['metadata'], indent=2)}")
        print(f"Text preview: {sample_chunk['text'][:200]}...")
    
    # Save the processed chunks to a JSON file for inspection
    output_file = os.path.join(project_root, "sample_data", "processed_chunks.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"\nSaved all processed chunks to {output_file}")
    
    # Print file organization recommendations
    recommendations = get_file_organization_recommendations()
    print("\nFile Organization Recommendations available in documentation")

if __name__ == "__main__":
    main()
