"""
Deployment Module for RAG Writing Assistant

This module provides deployment solutions for the RAG writing assistant.
"""

from .streamlit_app import main as run_streamlit_app

__all__ = ['run_streamlit_app']
