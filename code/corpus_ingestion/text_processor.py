"""
Text Processor Module for RAG Writing Assistant

This module handles the ingestion and processing of text files for the RAG-based writing assistant.
It includes functionality for reading files, chunking text, and attaching metadata.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextProcessor:
    """
    A class for processing text files into chunks suitable for embedding and retrieval.
    """
    
    def __init__(self, chunk_size: int = 750, chunk_overlap: int = 150):
        """
        Initialize the TextProcessor with chunking parameters.
        
        Args:
            chunk_size: Target size of each text chunk in words (default: 750)
            chunk_overlap: Number of words to overlap between chunks (default: 150)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized TextProcessor with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def read_file(self, file_path: str) -> str:
        """
        Read the content of a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            The content of the file as a string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.info(f"Successfully read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from the filename based on naming conventions.
        
        Args:
            filename: Name of the file (without path)
            
        Returns:
            Dictionary containing extracted metadata
        """
        # Remove file extension
        base_name = os.path.splitext(filename)[0]
        
        # Try to extract tags if they exist in the format "title [tag1, tag2]"
        tags = []
        title = base_name
        
        tag_match = re.search(r'(.*?)\s*\[(.*?)\]', base_name)
        if tag_match:
            title = tag_match.group(1).strip()
            tags = [tag.strip() for tag in tag_match.group(2).split(',')]
        
        # Determine content type based on filename patterns
        content_type = "general"
        if "essay" in base_name.lower():
            content_type = "essay"
        elif "reflection" in base_name.lower():
            content_type = "reflection"
        elif "podcast" in base_name.lower():
            content_type = "podcast"
        elif "substack" in base_name.lower() or "newsletter" in base_name.lower():
            content_type = "newsletter"
        
        metadata = {
            "title": title,
            "tags": tags,
            "content_type": content_type,
            "source_file": filename
        }
        
        logger.info(f"Extracted metadata from {filename}: {metadata}")
        return metadata
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks while preserving natural paragraph breaks.
        
        Args:
            text: The text content to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of dictionaries, each containing a text chunk and its metadata
        """
        # Split text into paragraphs
        paragraphs = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for paragraph in paragraphs:
            # Count words in paragraph
            paragraph_words = len(paragraph.split())
            
            # If adding this paragraph exceeds the chunk size and we already have content,
            # save the current chunk and start a new one
            if current_size + paragraph_words > self.chunk_size and current_chunk:
                # Join the current paragraphs into a single text
                chunk_text = "\n\n".join(current_chunk)
                
                # Create chunk with metadata
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_id": chunk_id,
                    "word_count": current_size
                })
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
                
                # Start a new chunk, potentially with overlap from the previous chunk
                if self.chunk_overlap > 0 and len(current_chunk) > 1:
                    # Keep the last paragraph for overlap
                    current_chunk = current_chunk[-1:]
                    current_size = len(current_chunk[0].split())
                else:
                    current_chunk = []
                    current_size = 0
                
                chunk_id += 1
            
            # Add the paragraph to the current chunk
            current_chunk.append(paragraph)
            current_size += paragraph_words
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "word_count": current_size
            })
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        logger.info(f"Created {len(chunks)} chunks from text with metadata: {metadata['title']}")
        return chunks
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a single file: read, extract metadata, and chunk.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of dictionaries, each containing a text chunk and its metadata
        """
        try:
            # Read the file
            content = self.read_file(file_path)
            
            # Extract metadata from filename
            filename = os.path.basename(file_path)
            metadata = self.extract_metadata_from_filename(filename)
            
            # Chunk the text
            chunks = self.chunk_text(content, metadata)
            
            return chunks
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return []
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Process all text files in a directory.
        
        Args:
            directory_path: Path to the directory containing text files
            
        Returns:
            List of dictionaries, each containing a text chunk and its metadata
        """
        all_chunks = []
        
        try:
            # Get all text files in the directory
            files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
            logger.info(f"Found {len(files)} text files in {directory_path}")
            
            for file in files:
                file_path = os.path.join(directory_path, file)
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
            
            logger.info(f"Processed {len(files)} files, created {len(all_chunks)} total chunks")
            return all_chunks
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return []


def get_file_organization_recommendations() -> str:
    """
    Provides recommendations for organizing and labeling text files.
    
    Returns:
        String containing recommendations
    """
    recommendations = """
# Best Practices for Organizing Text Files

## File Naming Conventions

For optimal processing and metadata extraction, consider using these naming patterns:

1. **Basic Format**: `Title [tag1, tag2, tag3].txt`
   - Example: `AI Ethics in Healthcare [ethics, healthcare, technology].txt`

2. **Content Type Indicators**: Include content type in the filename
   - Essays: `Essay - Title [tags].txt`
   - Reflections: `Reflection - Title [tags].txt`
   - Podcast Intros: `Podcast - Title [tags].txt`
   - Substack/Newsletter: `Substack - Title [tags].txt`

3. **Chronological Organization**: Add dates for time-sensitive content
   - `2023-05-15 - Newsletter - AI Updates [news, trends].txt`

## Content Structure

1. **Paragraphs**: Use blank lines between paragraphs for natural chunking
2. **Headers**: Use consistent header formatting (e.g., # for main headers)
3. **Sections**: Clearly delineate sections with headers or dividers

## Metadata Recommendations

Consider including these metadata elements at the top of your files:

```
Title: The Future of AI Education
Date: 2023-05-15
Tags: education, AI, future
Type: Essay
Summary: A brief exploration of how AI will transform educational systems.
```

## Folder Organization

1. **By Type**: Organize files in folders by content type
   - /essays/
   - /reflections/
   - /podcasts/
   - /newsletters/

2. **By Theme**: Alternatively, organize by thematic areas
   - /technology/
   - /philosophy/
   - /business/

## Additional Tips

1. **Consistency**: Maintain consistent formatting across all files
2. **File Size**: Keep individual files to a reasonable size (under 10,000 words)
3. **Plain Text**: Ensure files are saved as plain text (.txt) without formatting
4. **UTF-8 Encoding**: Use UTF-8 encoding to support all characters
5. **Backup**: Keep backups of your original files before processing
"""
    return recommendations
