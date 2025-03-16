"""
Root entry point for Streamlit Cloud deployment - Fixed Version

This script provides robust path handling and detailed diagnostics
to resolve module import issues in Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Enable debug mode to diagnose deployment issues
debug_mode = True

# Display diagnostic information
if debug_mode:
    st.write("# Deployment Diagnostics")
    st.write(f"Python version: {sys.version}")
    st.write(f"Current working directory: {os.getcwd()}")
    st.write(f"__file__: {__file__}")
    st.write(f"Script directory: {Path(__file__).parent.absolute()}")
    
    # Show directory contents
    current_dir = Path(__file__).parent.absolute()
    st.write("### Directory contents:")
    for item in current_dir.iterdir():
        if item.is_dir():
            st.write(f"📁 {item.name}")
            # Show subdirectory contents (1 level)
            try:
                for subitem in item.iterdir():
                    st.write(f"  - {subitem.name}")
            except PermissionError:
                st.write("  Permission denied")
        else:
            st.write(f"📄 {item.name}")
    
    st.write("### Current sys.path:")
    for path in sys.path:
        st.write(f"- {path}")

# Robust path setup - try multiple strategies
current_dir = Path(__file__).parent.absolute()

# Strategy 1: Add current directory to path
sys.path.insert(0, str(current_dir))

# Strategy 2: Look for rag_code in parent directories
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Strategy 3: Explicitly look for 'manus_rag_writing' directory (from logs)
mount_src_dir = Path("/mount/src") if os.path.exists("/mount/src") else None
if mount_src_dir and (mount_src_dir / "manus_rag_writing").exists():
    sys.path.insert(0, str(mount_src_dir / "manus_rag_writing"))
    if debug_mode:
        st.write("Found /mount/src/manus_rag_writing and added to path")

# Setup environment variables from Streamlit secrets
try:
    if 'api_keys' in st.secrets:
        if 'openai' in st.secrets.api_keys:
            os.environ['OPENAI_API_KEY'] = st.secrets.api_keys.openai
            if debug_mode:
                st.write("Set OpenAI API key from secrets")
        if 'anthropic' in st.secrets.api_keys:
            os.environ['ANTHROPIC_API_KEY'] = st.secrets.api_keys.anthropic
            if debug_mode:
                st.write("Set Anthropic API key from secrets")
except Exception as e:
    if debug_mode:
        st.error(f"Error setting up environment variables: {e}")

# Try direct import before importing the main app
if debug_mode:
    # Check if rag_code package is importable
    try:
        import rag_code
        st.success(f"Successfully imported rag_code from {rag_code.__file__}")
    except ImportError as e:
        st.error(f"Cannot import rag_code: {e}")
    
    # Check if specific modules are importable
    try:
        from rag_code.deployment import streamlit_app
        st.success("Successfully imported streamlit_app module")
    except ImportError as e:
        st.error(f"Cannot import streamlit_app module: {e}")

# Import the main function from the actual app
try:
    # Try multiple import strategies
    try:
        from rag_code.deployment.streamlit_app import main
        if debug_mode:
            st.success("Successfully imported main function from rag_code.deployment.streamlit_app")
    except ImportError:
        try:
            # Alternative import if package structure is different
            sys.path.append(str(current_dir / "rag_code" / "deployment"))
            from streamlit_app import main
            if debug_mode:
                st.success("Successfully imported main function from streamlit_app")
        except ImportError as e:
            if debug_mode:
                st.error(f"Error importing main function through alternative path: {e}")
            raise
except ImportError as e:
    if debug_mode:
        st.error(f"Error importing main function: {e}")
        
        # Check if rag_code directory exists
        rag_code_dir = current_dir / "rag_code"
        if rag_code_dir.exists():
            st.write(f"Contents of {rag_code_dir}:")
            for item in rag_code_dir.iterdir():
                if item.is_dir():
                    st.write(f"📁 {item.name}")
                    # List contents of this subdirectory
                    for subitem in item.iterdir():
                        st.write(f"  - {subitem.name}")
                else:
                    st.write(f"📄 {item.name}")
        else:
            st.error(f"rag_code directory not found at {rag_code_dir}")
            
            # Try to find rag_code directory anywhere on the path
            for path_dir in sys.path:
                path = Path(path_dir)
                if (path / "rag_code").exists():
                    st.write(f"Found rag_code in {path_dir}")
                    break
            else:
                st.write("Could not find rag_code directory anywhere on the path")
    
    st.error("Failed to initialize the application. Please check the diagnostics above to identify the path issues.")
    st.stop()  # Stop execution

# Run the app if everything is properly imported
if __name__ == "__main__":
    if debug_mode:
        st.write("### Application Ready")
        st.write("Diagnostics complete. The application can now start if you disable debug mode.")
        st.write("To proceed, set `debug_mode = False` at the top of the script.")
    else:
        main()
