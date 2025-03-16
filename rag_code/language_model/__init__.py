"""
Language Model Integration Module for RAG Writing Assistant

This module handles the integration with language models for generating content
based on retrieved context from the vector database.
"""

from .language_model import LanguageModelIntegration, get_language_model_recommendations

__all__ = ['LanguageModelIntegration', 'get_language_model_recommendations']
