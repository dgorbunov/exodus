import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from context_provider import ContextProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('grok_integration')

class GrokIntegration:
    """Handles integration with Grok AI for enhanced prompting with context."""
    
    def __init__(self, api_key: str = None, context_provider: Optional[ContextProvider] = None):
        """Initialize the Grok integration.
        
        Args:
            api_key: API key for Grok (if required)
            context_provider: ContextProvider instance for fetching relevant context
        """
        self.api_key = api_key or os.environ.get("GROK_API_KEY")
        self.context_provider = context_provider or ContextProvider()
        
        # Initialize context if not already done
        if not os.path.exists(self.context_provider.document_store.storage_dir) or \
           len(os.listdir(self.context_provider.document_store.storage_dir)) == 0:
            self.context_provider.initialize_context()
    
    def format_prompt_with_context(self, prompt: str, max_context_docs: int = 5) -> str:
        """Format a prompt with relevant context for Grok.
        
        Args:
            prompt: The user's original prompt
            max_context_docs: Maximum number of context documents to include
            
        Returns:
            Formatted prompt with context
        """
        # Get relevant context
        context = self.context_provider.get_context_for_prompt(prompt, max_documents=max_context_docs)
        
        # Format the prompt with context
        formatted_prompt = f"""I'm providing you with some relevant context to help answer the following question:

{prompt}

RELEVANT CONTEXT:
"""
        
        # Add each document to the context
        for i, doc in enumerate(context['documents']):
            formatted_prompt += f"\n[DOCUMENT {i+1}: {doc['title']} (Source: {doc['source']})]"
            formatted_prompt += f"\n{doc['content']}\n"
        
        # Add final instruction
        formatted_prompt += "\n\nBased on the above context and your knowledge, please answer the original question."
        
        return formatted_prompt
    
    def send_prompt_to_grok(self, prompt: str, include_context: bool = True, 
                           max_context_docs: int = 5) -> Dict[str, Any]:
        """Send a prompt to Grok with optional context enhancement.
        
        Args:
            prompt: The user's prompt
            include_context: Whether to include context from the ContextProvider
            max_context_docs: Maximum number of context documents to include
            
        Returns:
            Grok's response
        """
        if not self.api_key:
            logger.warning("No Grok API key provided. In a real implementation, this would fail.")
        
        # Format prompt with context if requested
        if include_context:
            formatted_prompt = self.format_prompt_with_context(prompt, max_context_docs)
        else:
            formatted_prompt = prompt
        
        logger.info(f"Sending prompt to Grok: {prompt[:50]}...")
        
        # In a real implementation, this would make an API call to Grok
        # For demonstration, we'll simulate a response
        
        # Simulated API call and response
        simulated_response = {
            "response": f"This is a simulated response from Grok for the prompt: '{prompt[:30]}...'",
            "prompt": formatted_prompt,
            "model": "grok-1",
            "timestamp": "2025-04-06T15:14:18-04:00"
        }
        
        return simulated_response
    
    def add_specific_context(self, prompt: str, context_type: str, context_id: str) -> str:
        """Add specific context to a prompt based on type and ID.
        
        Args:
            prompt: The original prompt
            context_type: Type of context ('nist', 'kali_tool', 'web')
            context_id: ID of the specific context (e.g., tool name, standard ID)
            
        Returns:
            Prompt with the specific context added
        """
        context_content = ""
        
        if context_type == "nist":
            nist_docs = self.context_provider.get_nist_standard(context_id)
            if nist_docs:
                context_content = "\n\nNIST STANDARD INFORMATION:\n"
                for doc in nist_docs:
                    context_content += f"\n{doc['title']}\n{doc['content']}\n"
        
        elif context_type == "kali_tool":
            tool_doc = self.context_provider.get_tool_documentation(context_id)
            if tool_doc:
                context_content = f"\n\nKALI TOOL DOCUMENTATION:\n\n{tool_doc['title']}\n{tool_doc['content']}\n"
        
        elif context_type == "web":
            web_results = self.context_provider.perform_web_search(context_id)
            if web_results:
                context_content = "\n\nWEB SEARCH RESULTS:\n"
                for result in web_results:
                    context_content += f"\n{result['title']}\n{result['content']}\nSource: {result['source']}\n"
        
        # Add the context to the prompt
        if context_content:
            enhanced_prompt = f"{prompt}\n{context_content}\n\nPlease use the above information in your response."
            return enhanced_prompt
        
        return prompt

    def batch_process_prompts(self, prompts: List[str], include_context: bool = True) -> List[Dict[str, Any]]:
        """Process multiple prompts in batch.
        
        Args:
            prompts: List of prompts to process
            include_context: Whether to include context
            
        Returns:
            List of responses
        """
        responses = []
        for prompt in prompts:
            response = self.send_prompt_to_grok(prompt, include_context)
            responses.append(response)
        return responses
