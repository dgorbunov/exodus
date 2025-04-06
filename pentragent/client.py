#!/usr/bin/env python3

import argparse
import json
import requests
import sys
from typing import Dict, Any, List, Optional

class PentragentClient:
    """Client for interacting with the Pentragent MCP Server."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url.rstrip('/')
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Execute a command in the Kali container.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command execution results
        """
        endpoint = f"{self.server_url}/execute_command"
        payload = {"command": command, "timeout": timeout}
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def scan_ip_range(self, ip_range: str, commands: List[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """Scan an IP range with multiple commands.
        
        Args:
            ip_range: IP range to scan (CIDR notation)
            commands: List of commands to execute
            timeout: Scan timeout in seconds
            
        Returns:
            Scan results
        """
        endpoint = f"{self.server_url}/scan_ip_range"
        payload = {"ip_range": ip_range, "timeout": timeout}
        
        if commands:
            payload["commands"] = commands
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def execute_tool(self, tool: str, target: str, options: Dict[str, Any] = None, timeout: int = 300) -> Dict[str, Any]:
        """Execute a specific security tool with customized parameters.
        
        Args:
            tool: Tool name (e.g., nmap, nikto, dirb)
            target: Target to scan
            options: Tool-specific options
            timeout: Tool execution timeout in seconds
            
        Returns:
            Tool execution results
        """
        endpoint = f"{self.server_url}/execute_tool"
        payload = {
            "tool": tool,
            "target": target,
            "timeout": timeout
        }
        
        if options:
            payload["options"] = options
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def send_prompt_to_grok(self, prompt: str, include_context: bool = True, 
                           max_context_docs: int = 5, context_type: str = None, 
                           context_id: str = None) -> Dict[str, Any]:
        """Send a prompt to Grok with optional context.
        
        Args:
            prompt: The prompt to send to Grok
            include_context: Whether to include context from the ContextProvider
            max_context_docs: Maximum number of context documents to include
            context_type: Specific context type to include ('nist', 'kali_tool', 'web')
            context_id: ID for specific context
            
        Returns:
            Grok's response
        """
        endpoint = f"{self.server_url}/grok/prompt"
        payload = {
            "prompt": prompt,
            "include_context": include_context,
            "max_context_docs": max_context_docs
        }
        
        if context_type and context_id:
            payload["context_type"] = context_type
            payload["context_id"] = context_id
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def search_documents(self, query: str, doc_type: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents in the document store.
        
        Args:
            query: Search query
            doc_type: Type of document to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        endpoint = f"{self.server_url}/documents/search"
        payload = {
            "query": query,
            "max_results": max_results
        }
        
        if doc_type:
            payload["doc_type"] = doc_type
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy.
        
        Returns:
            Health status
        """
        endpoint = f"{self.server_url}/health"
        response = requests.get(endpoint)
        response.raise_for_status()
        
        return response.json()

def format_json_output(data: Any) -> str:
    """Format JSON data for pretty printing.
    
    Args:
        data: Data to format
        
    Returns:
        Formatted string
    """
    return json.dumps(data, indent=2)

def main():
    """Main function for the client CLI."""
    parser = argparse.ArgumentParser(description="Pentragent MCP Client")
    parser.add_argument("--server", type=str, default="http://localhost:8000", help="MCP server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Execute command
    cmd_parser = subparsers.add_parser("exec", help="Execute a command in the Kali container")
    cmd_parser.add_argument("cmd", type=str, help="Command to execute")
    cmd_parser.add_argument("--timeout", type=int, default=60, help="Command timeout in seconds")
    
    # Scan IP range
    scan_parser = subparsers.add_parser("scan", help="Scan an IP range with multiple commands")
    scan_parser.add_argument("ip_range", type=str, help="IP range to scan (CIDR notation)")
    scan_parser.add_argument("--commands", type=str, nargs="*", help="Commands to execute")
    scan_parser.add_argument("--timeout", type=int, default=300, help="Scan timeout in seconds")
    
    # Execute tool
    tool_parser = subparsers.add_parser("tool", help="Execute a specific security tool")
    tool_parser.add_argument("tool", type=str, help="Tool name (e.g., nmap, nikto, dirb)")
    tool_parser.add_argument("target", type=str, help="Target to scan")
    tool_parser.add_argument("--options", type=str, help="Tool options as JSON string")
    tool_parser.add_argument("--timeout", type=int, default=300, help="Tool timeout in seconds")
    
    # Send prompt to Grok
    grok_parser = subparsers.add_parser("grok", help="Send a prompt to Grok")
    grok_parser.add_argument("prompt", type=str, help="Prompt to send to Grok")
    grok_parser.add_argument("--no-context", action="store_true", help="Disable context inclusion")
    grok_parser.add_argument("--max-docs", type=int, default=5, help="Maximum number of context documents")
    grok_parser.add_argument("--context-type", type=str, choices=["nist", "kali_tool", "web"], 
                           help="Specific context type to include")
    grok_parser.add_argument("--context-id", type=str, help="ID for specific context")
    
    # Search documents
    search_parser = subparsers.add_parser("search", help="Search documents in the document store")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--doc-type", type=str, help="Type of document to search for")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results")
    
    # Health check
    subparsers.add_parser("health", help="Check if the server is healthy")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = PentragentClient(args.server)
    
    try:
        if args.command == "exec":
            result = client.execute_command(args.cmd, args.timeout)
        
        elif args.command == "scan":
            result = client.scan_ip_range(args.ip_range, args.commands, args.timeout)
        
        elif args.command == "tool":
            options = {}
            if args.options:
                options = json.loads(args.options)
            
            result = client.execute_tool(args.tool, args.target, options, args.timeout)
        
        elif args.command == "grok":
            result = client.send_prompt_to_grok(
                args.prompt,
                not args.no_context,
                args.max_docs,
                args.context_type,
                args.context_id
            )
        
        elif args.command == "search":
            result = client.search_documents(args.query, args.doc_type, args.max_results)
        
        elif args.command == "health":
            result = client.health_check()
        
        print(format_json_output(result))
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
