# Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions for deploying your RAG Writing Assistant to Streamlit Cloud, making it accessible from anywhere with an internet connection.

## Prerequisites

1. A GitHub account
2. An OpenAI API key (or Anthropic API key)
3. Your text files (.txt format)

## Deployment Steps

### 1. Fork the Repository

1. Create a GitHub account if you don't have one at [github.com](https://github.com)
2. Go to the RAG Writing Assistant GitHub repository
3. Click the "Fork" button in the top-right corner to create your own copy

### 2. Set Up Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your forked repository
5. For the main file path, enter: `code/deployment/streamlit_app.py`
6. Click "Deploy"

### 3. Configure Secrets

Your API keys should never be stored in your code. Instead, use Streamlit's secrets management:

1. In your deployed app, click on the three dots (⋮) in the top-right corner
2. Select "Settings"
3. Go to the "Secrets" section
4. Add your API keys in the following format:

```toml
[api_keys]
openai = "your-openai-api-key-here"
anthropic = "your-anthropic-api-key-here"  # Optional
```

5. Click "Save"

### 4. Upload Your Text Files

Once your app is deployed:

1. Enter your API key in the sidebar
2. Click "Initialize System"
3. Use the file uploader in the sidebar to upload your text files one by one
4. After uploading all files, click "Reprocess All Files" to ensure everything is indexed properly

### 5. Share Your App (Optional)

By default, your Streamlit app is public and can be accessed by anyone with the URL. If you want to share it:

1. Copy the URL from your browser
2. Share it with anyone you want to give access to your writing assistant

If you want to make it private:

1. In your app settings, go to the "Sharing" section
2. Toggle "Public access" off
3. Add email addresses of people you want to give access to

## Updating Your App

### Adding New Text Files

To add new text files to your corpus:

1. Go to your deployed app
2. Use the file uploader in the sidebar to upload new files
3. The system will automatically process and index them

### Updating the Code

If you want to update the application code:

1. Make changes to your forked repository on GitHub
2. Streamlit Cloud will automatically detect the changes and redeploy your app

## Troubleshooting

### App Not Loading

- Check if your GitHub repository is public
- Verify that the main file path is correct
- Check the Streamlit Cloud logs for any errors

### API Key Issues

- Ensure your API key is correctly entered in the Secrets section
- Verify that your OpenAI account has sufficient credits

### File Processing Issues

- Make sure your files are in .txt format
- Check that your files follow the recommended naming convention
- Try reprocessing the corpus if files aren't being recognized properly

## Local Development (Alternative)

If you prefer to run the app locally:

1. Clone your forked repository
2. Install the required packages: `pip install -r code/deployment/requirements.txt`
3. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here  # Optional
   ```
4. Run the app: `streamlit run code/deployment/streamlit_app.py`

This will start the app on your local machine, typically at http://localhost:8501
