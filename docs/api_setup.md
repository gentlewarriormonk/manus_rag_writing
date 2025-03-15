# OpenAI API Key Setup Instructions

To use the vector database and embedding functionality, you'll need to set up an OpenAI API key. Follow these steps:

1. **Create an OpenAI account** if you don't already have one at [https://platform.openai.com/signup](https://platform.openai.com/signup)

2. **Generate an API key**:
   - Log in to your OpenAI account
   - Navigate to the API section
   - Click on "Create new secret key"
   - Copy the key (you won't be able to see it again)

3. **Set the API key as an environment variable**:
   - For Linux/Mac:
     ```bash
     export OPENAI_API_KEY="your-api-key-here"
     ```
   - For Windows (Command Prompt):
     ```
     set OPENAI_API_KEY=your-api-key-here
     ```
   - For Windows (PowerShell):
     ```
     $env:OPENAI_API_KEY="your-api-key-here"
     ```

4. **Alternative: Create a .env file**:
   - Create a file named `.env` in the project root directory
   - Add the following line:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```
   - The application will automatically load this file

## API Usage and Costs

- OpenAI's embedding models are charged per 1,000 tokens
- Current pricing for text-embedding-3-small: $0.02 per 1,000 tokens
- For a corpus of 20 text files (approximately 40,000 tokens), the embedding cost would be around $0.80
- Retrieval operations do not incur additional API costs

## Alternative Options

If you prefer not to use OpenAI's API, the system can be configured to use alternative embedding models:

1. **Sentence Transformers** (local, no API costs)
   - Requires more computational resources
   - May have lower quality embeddings

2. **Hugging Face Embedding Models** (local, no API costs)
   - Various models available with different quality/performance tradeoffs

The implementation can be modified to use these alternatives if preferred.
