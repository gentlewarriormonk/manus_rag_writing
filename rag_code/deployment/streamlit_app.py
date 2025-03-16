"""
Streamlit interface for the RAG Writing Assistant - Fixed Version

This module provides a Streamlit-based web interface for interacting with the RAG writing assistant.
It includes robust path handling and improved error handling for deployment environments.
"""

import os
import sys
import logging
import streamlit as st
from pathlib import Path
import tempfile
import time
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the absolute path to the project root with improved detection
current_file_path = Path(__file__).resolve()
# Detect if we're in the deployment subdirectory or directly in rag_code
if current_file_path.parent.name == "deployment":
    project_root = current_file_path.parent.parent.parent  # /path/to/project/rag_code/deployment/streamlit_app.py
else:
    project_root = current_file_path.parent  # /path/to/project/streamlit_app.py

# Print debug information to help troubleshoot
logger.info(f"Current file path: {current_file_path}")
logger.info(f"Project root path: {project_root}")
logger.info(f"Python path: {sys.path}")

# Add the project root to the Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.info(f"Added project root to sys.path: {project_root}")

# Also add the parent of rag_code
if current_file_path.parent.name == "deployment":
    parent_of_rag_code = project_root.parent
    if str(parent_of_rag_code) not in sys.path:
        sys.path.insert(0, str(parent_of_rag_code))
        logger.info(f"Added parent of rag_code to sys.path: {parent_of_rag_code}")

# Check for special Streamlit Cloud deployment path
mount_src_path = Path("/mount/src")
if mount_src_path.exists():
    # Look for our repository in the mount
    possible_repo_dirs = list(mount_src_path.glob("*rag*"))
    if possible_repo_dirs:
        repo_dir = possible_repo_dirs[0]
        logger.info(f"Found likely repository directory: {repo_dir}")
        if str(repo_dir) not in sys.path:
            sys.path.insert(0, str(repo_dir))
            logger.info(f"Added repository directory to sys.path: {repo_dir}")

# List the contents of the project root for debugging
logger.info(f"Directory contents of project root: {[x.name for x in project_root.iterdir()] if project_root.exists() else 'directory not found'}")

# Check if rag_code directory exists in the project root
rag_code_dir = project_root / "rag_code"
if rag_code_dir.exists():
    logger.info(f"rag_code directory found: {rag_code_dir}")
    logger.info(f"rag_code directory contents: {[x.name for x in rag_code_dir.iterdir()]}")
    
    # Make sure rag_code is in the path
    if str(rag_code_dir) not in sys.path:
        sys.path.insert(0, str(rag_code_dir))
        logger.info(f"Added rag_code directory to sys.path: {rag_code_dir}")
else:
    # Look for rag_code anywhere in the path
    logger.warning(f"rag_code directory not found at {rag_code_dir}")
    for path_dir in sys.path:
        path = Path(path_dir)
        if (path / "rag_code").exists():
            logger.info(f"Found rag_code in {path_dir}")
            rag_code_dir = path / "rag_code"
            break
    else:
        logger.error("Could not find rag_code directory anywhere on the path")

# Now try to import the RAG assistant with improved error handling
rag_assistant_imported = False

try:
    # First attempt - standard import
    from rag_code.rag_assistant import RAGWritingAssistant
    logger.info("Successfully imported RAGWritingAssistant via standard import")
    rag_assistant_imported = True
except ImportError as e:
    logger.warning(f"Standard import failed: {e}")
    
    # Second attempt - try dynamic import
    try:
        if rag_code_dir.exists() and (rag_code_dir / "rag_assistant.py").exists():
            logger.info("Attempting dynamic import...")
            spec = importlib.util.spec_from_file_location("rag_assistant", 
                                                         str(rag_code_dir / "rag_assistant.py"))
            rag_assistant_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rag_assistant_module)
            RAGWritingAssistant = rag_assistant_module.RAGWritingAssistant
            logger.info("Successfully imported RAGWritingAssistant via dynamic import")
            rag_assistant_imported = True
        else:
            logger.error(f"rag_assistant.py not found in {rag_code_dir}")
    except Exception as e2:
        logger.error(f"Dynamic import failed: {e2}")
        
        # Third attempt - look for it in the parent directory
        try:
            from rag_assistant import RAGWritingAssistant
            logger.info("Successfully imported RAGWritingAssistant from parent directory")
            rag_assistant_imported = True
        except ImportError as e3:
            logger.error(f"All import attempts failed: {e3}")

# Constants (configurable from environment variables for flexibility)
DEFAULT_CORPUS_DIR = os.environ.get('CORPUS_DIR', os.path.join(project_root, "corpus"))
DEFAULT_VECTOR_DB_DIR = os.environ.get('VECTOR_DB_DIR', os.path.join(project_root, "vector_db_data"))

# Create directories if they don't exist
os.makedirs(DEFAULT_CORPUS_DIR, exist_ok=True)
os.makedirs(DEFAULT_VECTOR_DB_DIR, exist_ok=True)

# Initialize session state
if 'rag_assistant' not in st.session_state:
    st.session_state.rag_assistant = None
if 'initialization_status' not in st.session_state:
    st.session_state.initialization_status = "not_started"
if 'corpus_stats' not in st.session_state:
    st.session_state.corpus_stats = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'import_error' not in st.session_state:
    st.session_state.import_error = not rag_assistant_imported

def initialize_assistant():
    """Initialize the RAG assistant"""
    try:
        if st.session_state.import_error:
            st.error("Cannot initialize: RAGWritingAssistant module could not be imported")
            st.session_state.initialization_status = "error"
            return
        
        st.session_state.initialization_status = "in_progress"
        
        # Get API keys from session state
        openai_api_key = st.session_state.get('openai_api_key', '')
        anthropic_api_key = st.session_state.get('anthropic_api_key', '')
        
        # Set environment variables
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        if anthropic_api_key:
            os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
        
        # Determine which API to use
        if openai_api_key:
            llm_provider = "openai"
            llm_model = "gpt-4o"
        elif anthropic_api_key:
            llm_provider = "anthropic"
            llm_model = "claude-3-sonnet-20240229"
        else:
            st.error("Please provide at least one API key (OpenAI or Anthropic)")
            st.session_state.initialization_status = "error"
            return
        
        # Initialize RAG assistant
        st.session_state.rag_assistant = RAGWritingAssistant(
            corpus_directory=DEFAULT_CORPUS_DIR,
            vector_db_directory=DEFAULT_VECTOR_DB_DIR,
            embedding_model="text-embedding-3-small",
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        # Process corpus
        num_chunks = st.session_state.rag_assistant.process_corpus()
        
        # Update status
        if num_chunks > 0:
            st.session_state.initialization_status = "complete"
            st.session_state.corpus_stats = st.session_state.rag_assistant.get_corpus_stats()
            logger.info(f"RAG assistant initialized with {num_chunks} text chunks")
        else:
            st.session_state.initialization_status = "complete"
            st.session_state.corpus_stats = {"corpus_files": 0, "vector_documents": 0, "content_types": {}}
            logger.info("RAG assistant initialized. No text files found in corpus directory.")
        
    except Exception as e:
        error_msg = str(e)
        st.session_state.initialization_status = "error"
        logger.error(f"Error initializing RAG assistant: {error_msg}")
        st.error(f"Error initializing system: {error_msg}")

# Rest of the functions remain unchanged
def upload_file(uploaded_file):
    """Upload and process a file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        
        # Save to corpus directory
        file_path = os.path.join(DEFAULT_CORPUS_DIR, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        # Process the file
        num_chunks = st.session_state.rag_assistant.add_file(file_path)
        
        # Save the updated state
        st.session_state.rag_assistant.save_state()
        
        # Update corpus stats
        st.session_state.corpus_stats = st.session_state.rag_assistant.get_corpus_stats()
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return num_chunks
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise

def reprocess_corpus():
    """Reprocess the entire corpus"""
    try:
        # Reprocess corpus
        num_chunks = st.session_state.rag_assistant.process_corpus(reprocess=True)
        
        # Save the updated state
        st.session_state.rag_assistant.save_state()
        
        # Update corpus stats
        st.session_state.corpus_stats = st.session_state.rag_assistant.get_corpus_stats()
        
        return num_chunks
    except Exception as e:
        logger.error(f"Error reprocessing corpus: {str(e)}")
        raise

def generate_content(query, style_adjustments=None):
    """Generate content based on query"""
    try:
        # Generate content
        content = st.session_state.rag_assistant.generate_content(query, style_adjustments)
        return content
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="RAG Writing Assistant",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS - same as before
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4a6fa5;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .status-complete {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-progress {
        color: #ffc107;
        font-weight: bold;
    }
    /* Other styles remain the same */
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">RAG Writing Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your personal writing assistant that captures your authentic voice</p>', unsafe_allow_html=True)
    
    # Display import error if present
    if st.session_state.import_error:
        st.error("""
        **Critical Error: The RAGWritingAssistant module could not be imported.**
        
        This is likely due to a Python path configuration issue. Please check:
        1. That the directory structure is correct
        2. That all required files are present
        3. That the Python path is configured correctly
        
        See logs for more details.
        """)
        
        # Show debugging info
        with st.expander("Show Debug Information"):
            st.write(f"Current file path: {current_file_path}")
            st.write(f"Project root path: {project_root}")
            st.write(f"Python path: {sys.path}")
            
            st.write("### Path Contents:")
            for path in sys.path:
                path_obj = Path(path)
                if path_obj.exists():
                    st.write(f"{path}: {[x.name for x in path_obj.iterdir()]}")
                else:
                    st.write(f"{path}: directory does not exist")
                    
            st.write("### Looking for rag_code:")
            for path in sys.path:
                path_obj = Path(path)
                if path_obj.exists() and (path_obj / "rag_code").exists():
                    st.write(f"Found rag_code in {path}")
                    st.write(f"Contents: {[x.name for x in (path_obj / 'rag_code').iterdir()]}")
        
    # Sidebar - API Setup and Corpus Management
    with st.sidebar:
        st.markdown('<h2 class="section-header">API Setup</h2>', unsafe_allow_html=True)
        
        # API key inputs
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        anthropic_api_key = st.text_input("Anthropic API Key (Optional)", type="password", help="Enter your Anthropic API key if you prefer to use Claude")
        
        if st.button("Save API Keys"):
            if openai_api_key or anthropic_api_key:
                st.session_state.openai_api_key = openai_api_key
                st.session_state.anthropic_api_key = anthropic_api_key
                st.session_state.api_key_set = True
                st.success("API keys saved!")
                
                # Reset initialization if keys changed
                if st.session_state.initialization_status == "complete":
                    st.session_state.initialization_status = "not_started"
                    st.experimental_rerun()
            else:
                st.error("Please provide at least one API key")
        
        # Rest of sidebar remains the same...
        # ...

    # Main content area - only show if no import error
    if not st.session_state.import_error:
        if not st.session_state.api_key_set:
            st.warning("Please enter your API key in the sidebar to get started")
        else:
            # Initialize button
            if st.session_state.initialization_status == "not_started":
                if st.button("Initialize System"):
                    with st.spinner("Initializing system..."):
                        initialize_assistant()
            
            # Rest of interface remains the same...
            # ...

if __name__ == "__main__":
    main()
