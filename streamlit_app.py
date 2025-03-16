"""
Root entry point for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Add the current directory to the Python path
# This is crucial for making imports work in Streamlit Cloud
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Display diagnostic information if there's an error
debug_mode = False  # Set to True temporarily to see more info

if debug_mode:
    st.write(f"Python version: {sys.version}")
    st.write(f"Current directory: {current_dir}")
    st.write(f"Directory contents:")
    for item in current_dir.iterdir():
        st.write(f"- {item.name}")
    st.write(f"Python path: {sys.path}")

# Setup environment variables from Streamlit secrets if they exist
try:
    if 'api_keys' in st.secrets:
        if 'openai' in st.secrets.api_keys:
            os.environ['OPENAI_API_KEY'] = st.secrets.api_keys.openai
        if 'anthropic' in st.secrets.api_keys:
            os.environ['ANTHROPIC_API_KEY'] = st.secrets.api_keys.anthropic
except Exception as e:
    if debug_mode:
        st.error(f"Error setting up environment variables: {e}")

# Import the main function from the actual app
try:
    from rag_code.deployment.streamlit_app import main
    if debug_mode:
        st.success("Successfully imported main function")
except ImportError as e:
    if debug_mode:
        st.error(f"Error importing main function: {e}")
        
        # List directory structure for rag_code if it exists
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
    
    # Continue with a simplified error message in production
    st.error("Failed to initialize the application. Please check your code and dependencies.")
    st.stop()  # Stop execution

# Run the app
if __name__ == "__main__":
    main()
