import os
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import docker
import ipaddress
import time
from context_provider import ContextProvider, Document
from grok_integration import GrokIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_server')

# Initialize FastAPI app
app = FastAPI(title="Pentragent MCP Server", 
              description="Master Control Program for pentragent with Grok integration")

# Docker container configuration
KALI_IMAGE = "kalilinux/kali-rolling"
CONTAINER_NAME = "pentragent-kali"

# Models for API requests and responses
class CommandRequest(BaseModel):
    command: str
    timeout: int = Field(default=60, description="Command timeout in seconds")

class ScanRequest(BaseModel):
    ip_range: str
    commands: List[str] = Field(default_factory=list)
    timeout: int = Field(default=300, description="Scan timeout in seconds")

class ToolRequest(BaseModel):
    tool: str
    target: str
    options: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=300, description="Tool timeout in seconds")

class GrokPromptRequest(BaseModel):
    prompt: str
    include_context: bool = Field(default=True, description="Whether to include context from the ContextProvider")
    max_context_docs: int = Field(default=5, description="Maximum number of context documents to include")
    context_type: Optional[str] = Field(default=None, description="Specific context type to include ('nist', 'kali_tool', 'web')")
    context_id: Optional[str] = Field(default=None, description="ID for specific context")

class DocSearchRequest(BaseModel):
    query: str
    doc_type: Optional[str] = Field(default=None, description="Type of document to search for")
    max_results: int = Field(default=10, description="Maximum number of results to return")

class MCPServer:
    """Master Control Program server for pentragent."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.docker_client = docker.from_env()
        self.context_provider = ContextProvider()
        self.grok_integration = GrokIntegration(context_provider=self.context_provider)
        
        # Initialize context
        self.context_provider.initialize_context()
    
    def ensure_container_running(self) -> str:
        """Ensure the Kali Linux container is running.
        
        Returns:
            Container ID
        """
        try:
            # Check if container already exists
            try:
                container = self.docker_client.containers.get(CONTAINER_NAME)
                if container.status != "running":
                    logger.info(f"Starting existing container {CONTAINER_NAME}")
                    container.start()
                return container.id
            except docker.errors.NotFound:
                # Container doesn't exist, create it
                logger.info(f"Creating new container {CONTAINER_NAME}")
                container = self.docker_client.containers.run(
                    KALI_IMAGE,
                    name=CONTAINER_NAME,
                    detach=True,
                    tty=True,
                    command="/bin/bash"
                )
                # Install basic tools (this would be more extensive in a real implementation)
                self.execute_command("apt-get update && apt-get install -y nmap nikto dirb")
                return container.id
        except Exception as e:
            logger.error(f"Error ensuring container is running: {e}")
            raise
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Execute a command in the Kali container.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command execution results
        """
        container_id = self.ensure_container_running()
        container = self.docker_client.containers.get(container_id)
        
        logger.info(f"Executing command: {command}")
        start_time = time.time()
        
        try:
            result = container.exec_run(command, tty=True, demux=True, timeout=timeout)
            stdout = result.output[0].decode('utf-8') if result.output[0] else ""
            stderr = result.output[1].decode('utf-8') if result.output[1] else ""
            
            execution_time = time.time() - start_time
            
            return {
                "command": command,
                "exit_code": result.exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "command": command,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def scan_ip_range(self, ip_range: str, commands: List[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """Scan an IP range with multiple commands.
        
        Args:
            ip_range: IP range to scan (CIDR notation)
            commands: List of commands to execute
            timeout: Scan timeout in seconds
            
        Returns:
            Scan results
        """
        # Validate IP range
        try:
            ipaddress.ip_network(ip_range)
        except ValueError as e:
            logger.error(f"Invalid IP range: {ip_range}")
            raise ValueError(f"Invalid IP range: {ip_range}")
        
        # Default commands if none provided
        if not commands:
            commands = [
                f"nmap -sS -T4 {ip_range}",
                f"nmap -sV -T4 {ip_range}"
            ]
        
        results = []
        for command in commands:
            result = self.execute_command(command, timeout)
            results.append(result)
        
        return {
            "ip_range": ip_range,
            "command_results": results
        }
    
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
        options = options or {}
        command = self._build_tool_command(tool, target, options)
        
        if not command:
            raise ValueError(f"Unsupported tool: {tool}")
        
        # Execute the command
        result = self.execute_command(command, timeout)
        
        # Add tool documentation to the result
        tool_doc = self.context_provider.get_tool_documentation(tool)
        if tool_doc:
            result["tool_documentation"] = tool_doc
        
        return result
    
    def _build_tool_command(self, tool: str, target: str, options: Dict[str, Any]) -> Optional[str]:
        """Build a command for a specific tool.
        
        Args:
            tool: Tool name
            target: Target to scan
            options: Tool-specific options
            
        Returns:
            Formatted command string or None if tool is not supported
        """
        if tool.lower() == "nmap":
            scan_type = options.get("scan_type", "-sS")
            ports = options.get("ports", "")
            if ports:
                ports = f"-p {ports}"
            timing = options.get("timing", "-T4")
            additional = options.get("additional", "")
            return f"nmap {scan_type} {timing} {ports} {additional} {target}".strip()
        
        elif tool.lower() == "nikto":
            ssl = "-ssl" if options.get("ssl", False) else ""
            port = f"-port {options.get('port')}" if options.get("port") else ""
            output = f"-output {options.get('output')}" if options.get("output") else ""
            return f"nikto -h {target} {ssl} {port} {output}".strip()
        
        elif tool.lower() == "dirb":
            wordlist = options.get("wordlist", "/usr/share/dirb/wordlists/common.txt")
            output = f"-o {options.get('output')}" if options.get("output") else ""
            delay = f"-z {options.get('delay')}" if options.get("delay") else ""
            return f"dirb {target} {wordlist} {output} {delay}".strip()
        
        return None
    
    def send_prompt_to_grok(self, prompt_request: GrokPromptRequest) -> Dict[str, Any]:
        """Send a prompt to Grok with optional context.
        
        Args:
            prompt_request: Prompt request details
            
        Returns:
            Grok's response
        """
        prompt = prompt_request.prompt
        
        # Add specific context if requested
        if prompt_request.context_type and prompt_request.context_id:
            prompt = self.grok_integration.add_specific_context(
                prompt, 
                prompt_request.context_type, 
                prompt_request.context_id
            )
        
        # Send to Grok
        response = self.grok_integration.send_prompt_to_grok(
            prompt,
            include_context=prompt_request.include_context,
            max_context_docs=prompt_request.max_context_docs
        )
        
        return response
    
    def search_documents(self, query: str, doc_type: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents in the document store.
        
        Args:
            query: Search query
            doc_type: Type of document to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        results = self.context_provider.document_store.search_documents(query, doc_type)
        return [doc.to_dict() for doc in results[:max_results]]

# Create MCP server instance
mcp_server = MCPServer()

# FastAPI dependency to get the MCP server
def get_mcp_server():
    return mcp_server

# API routes
@app.post("/execute_command", response_model=Dict[str, Any])
async def execute_command(command_request: CommandRequest, mcp: MCPServer = Depends(get_mcp_server)):
    """Execute a command in the Kali container."""
    try:
        result = mcp.execute_command(command_request.command, command_request.timeout)
        return result
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan_ip_range", response_model=Dict[str, Any])
async def scan_ip_range(scan_request: ScanRequest, mcp: MCPServer = Depends(get_mcp_server)):
    """Scan an IP range with multiple commands."""
    try:
        result = mcp.scan_ip_range(
            scan_request.ip_range, 
            scan_request.commands, 
            scan_request.timeout
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error scanning IP range: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute_tool", response_model=Dict[str, Any])
async def execute_tool(tool_request: ToolRequest, mcp: MCPServer = Depends(get_mcp_server)):
    """Execute a specific security tool with customized parameters."""
    try:
        result = mcp.execute_tool(
            tool_request.tool,
            tool_request.target,
            tool_request.options,
            tool_request.timeout
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grok/prompt", response_model=Dict[str, Any])
async def send_prompt_to_grok(prompt_request: GrokPromptRequest, mcp: MCPServer = Depends(get_mcp_server)):
    """Send a prompt to Grok with optional context."""
    try:
        result = mcp.send_prompt_to_grok(prompt_request)
        return result
    except Exception as e:
        logger.error(f"Error sending prompt to Grok: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/search", response_model=List[Dict[str, Any]])
async def search_documents(search_request: DocSearchRequest, mcp: MCPServer = Depends(get_mcp_server)):
    """Search documents in the document store."""
    try:
        results = mcp.search_documents(
            search_request.query,
            search_request.doc_type,
            search_request.max_results
        )
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Pentragent MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Run the FastAPI server
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
