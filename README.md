# RAG Writing Assistant

A fully-managed, retrieval-augmented generation (RAG) chatbot that leverages your personal writings to generate new content in your authentic voice.

## Overview

This system uses your existing text files (essays, reflections, podcast intros, newsletters) to create a personalized writing assistant that can generate content in your unique style. The assistant can also apply runtime style adjustments like "make this more humorous" or "add more formality."

Built with a focus on ease of use for those with minimal technical skills, this solution provides:

- Automatic processing of your text files
- Vector embedding and storage of your writing style
- Integration with state-of-the-art language models
- A simple, intuitive user interface
- Easy deployment options

## Features

- **Intelligent Text Processing**: Automatically chunks your writings while preserving natural paragraph breaks
- **Vector Database**: Stores semantic representations of your writing style
- **Style Mimicking**: Generates content that authentically sounds like you wrote it
- **Dynamic Style Adjustments**: Allows runtime modifications to style (formal, conversational, humorous, etc.)
- **Simple File Management**: Easy uploading and updating of your text corpus
- **Streamlit Deployment**: Simple cloud hosting with minimal technical requirements

## Getting Started

See the [Getting Started Guide](docs/getting_started.md) for quick setup instructions.

## Documentation

- [User Guide](docs/user_guide.md) - Comprehensive usage instructions
- [RAG Explanation](docs/rag_explanation.md) - Learn how RAG technology works
- [Implementation Guide](docs/implementation_guide.md) - Technical details of the system
- [Streamlit Deployment Guide](docs/streamlit_deployment.md) - Hosting instructions

## Requirements

- Python 3.8+
- OpenAI API key (or Anthropic API key)
- Your text files (.txt format)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r code/deployment/requirements.txt
   ```
3. Set up your API keys as environment variables or through the Streamlit interface

## Usage

### Local Development

Run the Streamlit app locally:

```
streamlit run code/deployment/streamlit_app.py
```

### Cloud Deployment

Follow the [Streamlit Deployment Guide](docs/streamlit_deployment.md) for cloud hosting instructions.

## File Organization

Your text files should follow this naming convention:

```
essay_1_title.txt
podcast_episode_2.txt
substack_3_topic.txt
uni_reflection_4.txt
```

The system automatically detects content types from these prefixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with LangChain, ChromaDB, and Streamlit
- Uses OpenAI and Anthropic APIs for language model capabilities
