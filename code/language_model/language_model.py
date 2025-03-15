"""
Language Model Integration Module for RAG Writing Assistant

This module handles the integration with language models for generating content
based on retrieved context from the vector database.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LanguageModelIntegration:
    """
    A class for integrating language models with the RAG system.
    """
    
    def __init__(self, 
                 model_provider: str = "openai",
                 model_name: str = "gpt-4o",
                 temperature: float = 0.7,
                 max_tokens: int = 1000):
        """
        Initialize the LanguageModelIntegration with model settings.
        
        Args:
            model_provider: Provider of the language model ("openai" or "anthropic")
            model_name: Name of the model to use
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize language model
        self.llm = self._initialize_llm()
        
        logger.info(f"Initialized LanguageModelIntegration with provider={model_provider}, model={model_name}")
    
    def _initialize_llm(self):
        """
        Initialize the language model based on the provider.
        
        Returns:
            An initialized language model
        """
        try:
            if self.model_provider.lower() == "openai":
                llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info(f"Initialized OpenAI model: {self.model_name}")
            elif self.model_provider.lower() == "anthropic":
                llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info(f"Initialized Anthropic model: {self.model_name}")
            else:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")
            
            return llm
        except Exception as e:
            logger.error(f"Error initializing language model: {str(e)}")
            raise
    
    def create_rag_chain(self, retriever_func):
        """
        Create a RAG chain that retrieves context and generates responses.
        
        Args:
            retriever_func: Function that takes a query and returns relevant documents
            
        Returns:
            A callable chain that generates responses based on retrieved context
        """
        # Define the prompt template
        prompt = ChatPromptTemplate.from_template("""
You are a writing assistant that mimics the style and voice of the user based on their previous writings.
Your goal is to generate new content that sounds authentically like the user wrote it.

Here are relevant examples of the user's writing style:

{context}

Based on these examples, please write a response to the following request in the user's authentic voice:

{query}

{style_guidance}

Remember to maintain the user's unique voice, vocabulary choices, sentence structures, and thematic preferences.
""")
        
        # Create the RAG chain
        rag_chain = (
            {"context": retriever_func, "query": RunnablePassthrough(), "style_guidance": lambda x: self._get_style_guidance(x)}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def _get_style_guidance(self, query):
        """
        Extract style guidance from the query if present.
        
        Args:
            query: The user query
            
        Returns:
            Style guidance string or empty string
        """
        # Look for style instructions in brackets or parentheses
        style_markers = [
            (r'\[make this (.*?)\]', r'Style adjustment: \1'),
            (r'\(make this (.*?)\)', r'Style adjustment: \1'),
            (r'make this (more|less) (\w+)', r'Style adjustment: \1 \2')
        ]
        
        guidance = ""
        
        for pattern, replacement in style_markers:
            import re
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                guidance = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
                break
        
        if guidance:
            return f"Style guidance: {guidance}"
        return ""
    
    def generate_with_style(self, query: str, context_docs: List[Dict[str, Any]], style_adjustments: Optional[str] = None) -> str:
        """
        Generate content based on query and context with optional style adjustments.
        
        Args:
            query: The user query
            context_docs: List of context documents
            style_adjustments: Optional style adjustment instructions
            
        Returns:
            Generated content
        """
        try:
            # Format context from documents
            context = self._format_context_from_docs(context_docs)
            
            # Add style adjustments if provided
            style_guidance = ""
            if style_adjustments:
                style_guidance = f"Style guidance: {style_adjustments}"
            
            # Create the prompt
            prompt = f"""
You are a writing assistant that mimics the style and voice of the user based on their previous writings.
Your goal is to generate new content that sounds authentically like the user wrote it.

Here are relevant examples of the user's writing style:

{context}

Based on these examples, please write a response to the following request in the user's authentic voice:

{query}

{style_guidance}

Remember to maintain the user's unique voice, vocabulary choices, sentence structures, and thematic preferences.
"""
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            logger.info(f"Generated content for query: {query[:50]}...")
            return content
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def _format_context_from_docs(self, docs: List[Dict[str, Any]]) -> str:
        """
        Format context from retrieved documents.
        
        Args:
            docs: List of document dictionaries
            
        Returns:
            Formatted context string
        """
        formatted_context = ""
        
        for i, doc in enumerate(docs):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            content_type = metadata.get("content_type", "unknown")
            title = metadata.get("title", f"Document {i+1}")
            
            formatted_context += f"--- Example {i+1} (Content type: {content_type}) ---\n"
            formatted_context += f"Title: {title}\n\n"
            formatted_context += f"{text}\n\n"
        
        return formatted_context


def get_language_model_recommendations() -> str:
    """
    Provides recommendations for language models.
    
    Returns:
        String containing recommendations
    """
    recommendations = """
# Language Model Recommendations

## Comparison of OpenAI vs Anthropic Models

### OpenAI Models

1. **GPT-4o** (Recommended)
   - Strengths: Excellent at mimicking writing styles, strong context understanding
   - Best for: General purpose writing assistance, style mimicking
   - Cost: Higher than GPT-3.5 but justified by quality

2. **GPT-4 Turbo**
   - Strengths: Large context window, good for longer documents
   - Best for: When handling very long contexts or generating longer outputs
   - Cost: Similar to GPT-4o

3. **GPT-3.5 Turbo**
   - Strengths: Cost-effective, fast responses
   - Best for: Budget-conscious implementations, simpler writing tasks
   - Limitations: Less nuanced style mimicking, may miss subtle voice characteristics

### Anthropic Models

1. **Claude 3 Sonnet**
   - Strengths: Excellent writing quality, nuanced understanding of style
   - Best for: High-quality writing assistance, especially for literary styles
   - Cost: Competitive with GPT-4

2. **Claude 3 Haiku**
   - Strengths: Faster responses, good balance of quality and cost
   - Best for: When response speed is important
   - Limitations: Less sophisticated than Sonnet for complex writing styles

## Selection Criteria

When choosing a language model, consider:

1. **Style Mimicking Ability**: How well does it capture and reproduce the user's unique voice?
2. **Context Understanding**: How effectively does it use the retrieved examples?
3. **Cost**: What is the API usage cost for your expected volume?
4. **Response Speed**: How quickly does it generate responses?
5. **Reliability**: How consistent is the quality of outputs?

## Recommendation

For this RAG-based writing assistant, we recommend:
- **Primary choice**: OpenAI's GPT-4o
- **Alternative**: Claude 3 Sonnet if preferred

Both models demonstrate excellent ability to mimic writing styles when provided with good examples. The final choice may depend on:
- Personal preference for output style
- API pricing considerations
- Integration simplicity
"""
    return recommendations
