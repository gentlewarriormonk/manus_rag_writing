"""
Root entry point for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
# This makes the rag_code package importable
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the main function from the actual app
try:
    from rag_code.deployment.streamlit_app import main
    print("Successfully imported main function from rag_code.deployment.streamlit_app")
except ImportError as e:
    print(f"Error importing main function: {e}")
    print(f"Current sys.path: {sys.path}")
    # List files in current directory for debugging
    print(f"Files in {current_dir}:")
    for file in os.listdir(current_dir):
        print(f"  - {file}")
    # List files in rag_code directory if it exists
    rag_code_dir = current_dir / "rag_code"
    if rag_code_dir.exists():
        print(f"Files in {rag_code_dir}:")
        for file in os.listdir(rag_code_dir):
            print(f"  - {file}")
    raise

# Run the app
if __name__ == "__main__":
    main()
