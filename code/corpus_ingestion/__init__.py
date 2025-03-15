"""
Corpus Ingestion Module for RAG Writing Assistant

This module handles the ingestion and processing of text files for the RAG-based writing assistant.
"""

from .text_processor import TextProcessor, get_file_organization_recommendations

__all__ = ['TextProcessor', 'get_file_organization_recommendations']
