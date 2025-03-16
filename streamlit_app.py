"""
Root entry point for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

# Add the repository root to the Python path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

# Import the main function from the actual app
from rag_code.deployment.streamlit_app import main

# Run the app
if __name__ == "__main__":
    main()
