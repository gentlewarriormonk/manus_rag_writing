"""
Flask-based web interface for the RAG Writing Assistant

This module provides a web interface for interacting with the RAG writing assistant.
"""

import os
import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path
import threading
import time

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from code.rag_assistant import RAGWritingAssistant

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

# Global variables
PROJECT_ROOT = Path(__file__).parent.parent
CORPUS_DIR = os.path.join(PROJECT_ROOT, "corpus")
VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "vector_db_data")
ALLOWED_EXTENSIONS = {'txt'}

# Create directories if they don't exist
os.makedirs(CORPUS_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Initialize RAG assistant
rag_assistant = None
initialization_status = {"status": "not_started", "message": "System not initialized"}
initialization_thread = None

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_assistant():
    """Initialize the RAG assistant in a separate thread"""
    global rag_assistant, initialization_status, initialization_thread
    
    def init_thread():
        global rag_assistant, initialization_status
        try:
            initialization_status = {"status": "in_progress", "message": "Initializing system..."}
            
            # Initialize RAG assistant
            rag_assistant = RAGWritingAssistant(
                corpus_directory=CORPUS_DIR,
                vector_db_directory=VECTOR_DB_DIR,
                embedding_model="text-embedding-3-small",
                llm_provider="openai",
                llm_model="gpt-4o"
            )
            
            # Process corpus
            initialization_status = {"status": "in_progress", "message": "Processing corpus..."}
            num_chunks = rag_assistant.process_corpus()
            
            if num_chunks > 0:
                initialization_status = {"status": "complete", "message": f"System initialized with {num_chunks} text chunks"}
            else:
                initialization_status = {"status": "complete", "message": "System initialized. No text files found in corpus directory."}
            
            logger.info(f"RAG assistant initialized: {initialization_status['message']}")
        except Exception as e:
            error_msg = str(e)
            initialization_status = {"status": "error", "message": f"Error initializing system: {error_msg}"}
            logger.error(f"Error initializing RAG assistant: {error_msg}")
    
    # Start initialization in a separate thread
    initialization_thread = threading.Thread(target=init_thread)
    initialization_thread.daemon = True
    initialization_thread.start()

@app.route('/')
def index():
    """Render the main page"""
    global initialization_status
    
    # Start initialization if not started
    if initialization_status["status"] == "not_started":
        initialize_assistant()
    
    # Get corpus stats if available
    corpus_stats = None
    if rag_assistant and initialization_status["status"] == "complete":
        try:
            corpus_stats = rag_assistant.get_corpus_stats()
        except Exception as e:
            logger.error(f"Error getting corpus stats: {str(e)}")
    
    return render_template('index.html', 
                          initialization_status=initialization_status,
                          corpus_stats=corpus_stats)

@app.route('/status')
def status():
    """Get the current initialization status"""
    global initialization_status
    return jsonify(initialization_status)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate content based on user query"""
    global rag_assistant, initialization_status
    
    if not rag_assistant or initialization_status["status"] != "complete":
        return jsonify({"error": "System not fully initialized yet"}), 503
    
    try:
        data = request.json
        query = data.get('query', '')
        style_adjustments = data.get('style_adjustments', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Generate content
        content = rag_assistant.generate_content(query, style_adjustments)
        
        return jsonify({"content": content})
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({"error": f"Error generating content: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a text file to the corpus"""
    global rag_assistant, initialization_status
    
    if not rag_assistant or initialization_status["status"] != "complete":
        return jsonify({"error": "System not fully initialized yet"}), 503
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file extension is allowed
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Please upload .txt files only"}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(CORPUS_DIR, filename)
        file.save(file_path)
        
        # Process the file
        num_chunks = rag_assistant.add_file(file_path)
        
        # Save the updated state
        rag_assistant.save_state()
        
        return jsonify({"success": True, "message": f"File uploaded and processed into {num_chunks} chunks"})
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500

@app.route('/reprocess', methods=['POST'])
def reprocess_corpus():
    """Reprocess the entire corpus"""
    global rag_assistant, initialization_status
    
    if not rag_assistant or initialization_status["status"] != "complete":
        return jsonify({"error": "System not fully initialized yet"}), 503
    
    try:
        # Reprocess corpus
        num_chunks = rag_assistant.process_corpus(reprocess=True)
        
        # Save the updated state
        rag_assistant.save_state()
        
        return jsonify({"success": True, "message": f"Corpus reprocessed into {num_chunks} chunks"})
    except Exception as e:
        logger.error(f"Error reprocessing corpus: {str(e)}")
        return jsonify({"error": f"Error reprocessing corpus: {str(e)}"}), 500

@app.route('/corpus')
def corpus():
    """Get information about the corpus"""
    global rag_assistant, initialization_status
    
    if not rag_assistant or initialization_status["status"] != "complete":
        return jsonify({"error": "System not fully initialized yet"}), 503
    
    try:
        # Get corpus stats
        stats = rag_assistant.get_corpus_stats()
        
        # Get list of files
        files = []
        if os.path.exists(CORPUS_DIR):
            files = [f for f in os.listdir(CORPUS_DIR) if f.endswith('.txt')]
        
        return jsonify({
            "stats": stats,
            "files": files
        })
    except Exception as e:
        logger.error(f"Error getting corpus info: {str(e)}")
        return jsonify({"error": f"Error getting corpus info: {str(e)}"}), 500

def run_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask app"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_app(debug=True)
