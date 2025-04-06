import os
import json
import requests
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('context_provider')

@dataclass
class Document:
    """Represents a document with content and metadata."""
    title: str
    content: str
    source: str
    doc_type: str
    timestamp: float
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary format."""
        return {
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'doc_type': self.doc_type,
            'timestamp': self.timestamp,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary."""
        return cls(
            title=data['title'],
            content=data['content'],
            source=data['source'],
            doc_type=data['doc_type'],
            timestamp=data['timestamp'],
            metadata=data.get('metadata', {})
        )

class DocumentStore:
    """Manages document storage and retrieval."""
    def __init__(self, storage_dir: str = 'documents'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
    def save_document(self, document: Document) -> str:
        """Save document to storage."""
        # Create a filename based on document title and timestamp
        filename = f"{document.doc_type}_{int(document.timestamp)}_{document.title.replace(' ', '_')[:50]}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(document.to_dict(), f, indent=2)
        
        return filepath
    
    def load_document(self, filepath: str) -> Document:
        """Load document from storage."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return Document.from_dict(data)
    
    def list_documents(self, doc_type: Optional[str] = None) -> List[str]:
        """List all document filepaths, optionally filtered by type."""
        if not os.path.exists(self.storage_dir):
            return []
        
        files = os.listdir(self.storage_dir)
        if doc_type:
            files = [f for f in files if f.startswith(f"{doc_type}_")]
        
        return [os.path.join(self.storage_dir, f) for f in files]
    
    def search_documents(self, query: str, doc_type: Optional[str] = None) -> List[Document]:
        """Basic search functionality across documents."""
        results = []
        filepaths = self.list_documents(doc_type)
        
        for filepath in filepaths:
            doc = self.load_document(filepath)
            # Simple string matching for now
            if query.lower() in doc.title.lower() or query.lower() in doc.content.lower():
                results.append(doc)
        
        return results

class NISTDocumentFetcher:
    """Fetches NIST security standards and documentation."""
    def __init__(self, document_store: DocumentStore):
        self.document_store = document_store
        self.base_url = "https://csrc.nist.gov/CSRC/media/Publications/sp/800-53/rev-5/download/"
        
    def fetch_nist_800_53(self) -> List[Document]:
        """Fetch NIST 800-53 security controls."""
        logger.info("Fetching NIST 800-53 security controls")
        # In a real implementation, this would download and parse the actual document
        # For demonstration, we'll create a simplified version
        
        controls = [
            {
                "id": "AC-1",
                "title": "Access Control Policy and Procedures",
                "description": "The organization develops, documents, and disseminates an access control policy..."
            },
            {
                "id": "AC-2",
                "title": "Account Management",
                "description": "The organization manages information system accounts, including establishing..."
            },
            # More controls would be added in a real implementation
        ]
        
        documents = []
        for control in controls:
            doc = Document(
                title=f"NIST 800-53 Control: {control['id']} - {control['title']}",
                content=control['description'],
                source="NIST 800-53 Rev 5",
                doc_type="nist_standard",
                timestamp=time.time(),
                metadata={"control_id": control['id']}
            )
            self.document_store.save_document(doc)
            documents.append(doc)
        
        return documents
    
    def fetch_nist_cybersecurity_framework(self) -> List[Document]:
        """Fetch NIST Cybersecurity Framework."""
        logger.info("Fetching NIST Cybersecurity Framework")
        # Simplified implementation
        
        framework_functions = [
            {
                "id": "ID",
                "name": "Identify",
                "description": "Develop organizational understanding to manage cybersecurity risk..."
            },
            {
                "id": "PR",
                "name": "Protect",
                "description": "Develop and implement appropriate safeguards to ensure delivery of critical services..."
            },
            {
                "id": "DE",
                "name": "Detect",
                "description": "Develop and implement appropriate activities to identify the occurrence of a cybersecurity event..."
            },
            {
                "id": "RS",
                "name": "Respond",
                "description": "Develop and implement appropriate activities to take action regarding a detected cybersecurity incident..."
            },
            {
                "id": "RC",
                "name": "Recover",
                "description": "Develop and implement appropriate activities to maintain plans for resilience..."
            }
        ]
        
        documents = []
        for function in framework_functions:
            doc = Document(
                title=f"NIST CSF Function: {function['id']} - {function['name']}",
                content=function['description'],
                source="NIST Cybersecurity Framework",
                doc_type="nist_standard",
                timestamp=time.time(),
                metadata={"function_id": function['id']}
            )
            self.document_store.save_document(doc)
            documents.append(doc)
        
        return documents

class KaliDocumentFetcher:
    """Fetches Kali Linux package documentation."""
    def __init__(self, document_store: DocumentStore):
        self.document_store = document_store
        
    def fetch_tool_documentation(self, tool_name: str) -> Optional[Document]:
        """Fetch documentation for a specific Kali tool."""
        logger.info(f"Fetching documentation for Kali tool: {tool_name}")
        
        # In a real implementation, this would query Kali's documentation or man pages
        # For demonstration, we'll use a simplified approach with common tools
        
        tool_docs = {
            "nmap": {
                "description": "Nmap ('Network Mapper') is a free and open source utility for network discovery and security auditing.",
                "usage": "nmap [Scan Type] [Options] {target}",
                "common_options": "-sS (TCP SYN scan), -sU (UDP scan), -p (port specification), -A (aggressive scan)"
            },
            "metasploit": {
                "description": "The Metasploit Framework is a penetration testing platform that enables you to find, exploit, and validate vulnerabilities.",
                "usage": "msfconsole, use <exploit>, set <options>, exploit",
                "common_options": "show exploits, show payloads, info, search <keyword>"
            },
            "nikto": {
                "description": "Nikto is an Open Source web server scanner which performs comprehensive tests against web servers for multiple items.",
                "usage": "nikto -h <host>",
                "common_options": "-ssl, -port <port>, -output <file>"
            },
            "dirb": {
                "description": "DIRB is a Web Content Scanner that looks for existing (and/or hidden) Web Objects by launching a dictionary-based attack.",
                "usage": "dirb <url> [wordlist_file]",
                "common_options": "-o <output_file>, -z <milliseconds> (add milliseconds delay between requests)"
            }
        }
        
        if tool_name.lower() in tool_docs:
            tool_info = tool_docs[tool_name.lower()]
            doc = Document(
                title=f"Kali Linux Tool: {tool_name}",
                content=f"Description: {tool_info['description']}\n\nUsage: {tool_info['usage']}\n\nCommon Options: {tool_info['common_options']}",
                source="Kali Linux Documentation",
                doc_type="kali_tool",
                timestamp=time.time(),
                metadata={"tool_name": tool_name}
            )
            self.document_store.save_document(doc)
            return doc
        
        return None
    
    def fetch_all_common_tools(self) -> List[Document]:
        """Fetch documentation for common Kali Linux tools."""
        logger.info("Fetching documentation for common Kali Linux tools")
        
        common_tools = ["nmap", "metasploit", "nikto", "dirb", "hydra", "john", "aircrack-ng", "wireshark"]
        documents = []
        
        for tool in common_tools:
            doc = self.fetch_tool_documentation(tool)
            if doc:
                documents.append(doc)
        
        return documents

class WebSearchProvider:
    """Provides web search capabilities for additional information."""
    def __init__(self, document_store: DocumentStore, api_key: Optional[str] = None):
        self.document_store = document_store
        self.api_key = api_key
        
    def search(self, query: str, num_results: int = 5) -> List[Document]:
        """Perform a web search and store results as documents."""
        logger.info(f"Performing web search for: {query}")
        
        # In a real implementation, this would use a search API like Google, Bing, or DuckDuckGo
        # For demonstration, we'll simulate search results
        
        # Note: In a production environment, you would need to implement a proper API call
        # to a search engine service using the API key
        
        # Simulated search results
        search_results = [
            {
                "title": f"Search Result 1 for '{query}'",
                "snippet": f"This is a simulated search result for the query '{query}'. In a real implementation, this would contain actual content from a web search.",
                "url": f"https://example.com/result1?q={query}"
            },
            {
                "title": f"Search Result 2 for '{query}'",
                "snippet": f"Another simulated search result for '{query}'. This would typically contain a snippet from the webpage.",
                "url": f"https://example.com/result2?q={query}"
            },
            # More results would be included in a real implementation
        ]
        
        documents = []
        for i, result in enumerate(search_results[:num_results]):
            doc = Document(
                title=result["title"],
                content=result["snippet"],
                source=result["url"],
                doc_type="web_search",
                timestamp=time.time(),
                metadata={"query": query, "rank": i+1}
            )
            self.document_store.save_document(doc)
            documents.append(doc)
        
        return documents
    
    def fetch_webpage_content(self, url: str) -> Optional[Document]:
        """Fetch and store the content of a specific webpage."""
        logger.info(f"Fetching webpage content from: {url}")
        
        try:
            # In a real implementation, this would use requests or a similar library
            # to fetch the actual webpage content
            # For demonstration, we'll simulate the content
            
            # Simulated webpage content
            title = f"Webpage at {url}"
            content = f"This is simulated content for the webpage at {url}. In a real implementation, this would contain the actual HTML content parsed into readable text."
            
            doc = Document(
                title=title,
                content=content,
                source=url,
                doc_type="webpage",
                timestamp=time.time(),
                metadata={"url": url}
            )
            self.document_store.save_document(doc)
            return doc
            
        except Exception as e:
            logger.error(f"Error fetching webpage content from {url}: {e}")
            return None

class ContextProvider:
    """Main class for providing context to Grok."""
    def __init__(self, storage_dir: str = 'documents', web_search_api_key: Optional[str] = None):
        self.document_store = DocumentStore(storage_dir)
        self.nist_fetcher = NISTDocumentFetcher(self.document_store)
        self.kali_fetcher = KaliDocumentFetcher(self.document_store)
        self.web_search = WebSearchProvider(self.document_store, web_search_api_key)
    
    def initialize_context(self):
        """Initialize context with basic NIST and Kali documentation."""
        logger.info("Initializing context with basic documentation")
        
        # Fetch NIST standards
        self.nist_fetcher.fetch_nist_800_53()
        self.nist_fetcher.fetch_nist_cybersecurity_framework()
        
        # Fetch common Kali tool documentation
        self.kali_fetcher.fetch_all_common_tools()
        
        logger.info("Context initialization complete")
    
    def get_context_for_prompt(self, prompt: str, max_documents: int = 10) -> Dict[str, Any]:
        """Get relevant context for a given prompt to send to Grok."""
        logger.info(f"Getting context for prompt: {prompt}")
        
        # Search existing documents first
        local_results = self.document_store.search_documents(prompt)
        
        # If we don't have enough local results, perform a web search
        if len(local_results) < max_documents:
            web_results = self.web_search.search(prompt, num_results=max_documents-len(local_results))
            all_results = local_results + web_results
        else:
            all_results = local_results[:max_documents]
        
        # Format context for Grok
        context = {
            "documents": [doc.to_dict() for doc in all_results],
            "timestamp": time.time(),
            "query": prompt
        }
        
        return context
    
    def get_tool_documentation(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get documentation for a specific Kali tool."""
        doc = self.kali_fetcher.fetch_tool_documentation(tool_name)
        if doc:
            return doc.to_dict()
        return None
    
    def get_nist_standard(self, standard_id: str) -> List[Dict[str, Any]]:
        """Get NIST standard by ID (e.g., '800-53', 'CSF')."""
        results = self.document_store.search_documents(standard_id, doc_type="nist_standard")
        return [doc.to_dict() for doc in results]
    
    def perform_web_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a web search for additional information."""
        results = self.web_search.search(query, num_results=num_results)
        return [doc.to_dict() for doc in results]
