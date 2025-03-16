"""
Vector Database Module for RAG Writing Assistant

This module handles the vector embeddings and similarity search functionality.
"""

from .vector_store import VectorStore, get_embedding_model_recommendations

__all__ = ['VectorStore', 'get_embedding_model_recommendations']
