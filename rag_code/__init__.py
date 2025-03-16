"""
RAG Writing Assistant package
"""

# Make sure the modules are importable
try:
    from . import corpus_ingestion
    from . import vector_db
    from . import language_model
    from .rag_assistant import RAGWritingAssistant

    __all__ = ['RAGWritingAssistant', 'corpus_ingestion', 'vector_db', 'language_model']
    
except ImportError as e:
    print(f"Warning: Not all modules could be imported in rag_code/__init__.py: {e}")
