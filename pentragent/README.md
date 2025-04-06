# Pentragent MCP Server with Grok Integration

The Pentragent Master Control Program (MCP) is a comprehensive security operations platform that combines a Kali Linux environment with AI-powered analysis through Grok integration. This system allows you to execute security tools, scan IP ranges, and leverage AI with enhanced context from NIST security standards, Kali Linux tool documentation, and web searches.

## Features

### Security Operations
- **Command Execution**: Run arbitrary commands in a Kali Linux container
- **IP Range Scanning**: Scan IP ranges with customizable commands
- **Security Tool Integration**: Execute specific security tools (nmap, nikto, dirb) with customizable parameters

### AI Integration
- **Grok Integration**: Send prompts to Grok with enhanced context
- **Context Provision**: Provide NIST documents, Kali Linux package documentation, and web search results to Grok
- **Document Management**: Store and search security-related documents

## Components

### MCP Server (main.py)
The core server component that provides RESTful API endpoints for all functionality.

### Context Provider (context_provider.py)
Manages document storage and retrieval, including:
- NIST security standards (800-53, Cybersecurity Framework)
- Kali Linux tool documentation
- Web search results

### Grok Integration (grok_integration.py)
Handles communication with Grok, including:
- Formatting prompts with relevant context
- Sending prompts to Grok
- Processing responses

### Client (client.py)
A command-line client for interacting with the MCP server.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pentragent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
export GROK_API_KEY=your_api_key_here
```

## Usage

### Starting the Server

```bash
python main.py --host 0.0.0.0 --port 8000 --reload
```

### Using the Client

#### Execute a Command
```bash
python client.py exec "nmap -sS -T4 192.168.1.1"
```

#### Scan an IP Range
```bash
python client.py scan "192.168.1.0/24" --commands "nmap -sS -T4 192.168.1.0/24" "nmap -sV 192.168.1.0/24"
```

#### Execute a Security Tool
```bash
python client.py tool nmap "192.168.1.1" --options '{"scan_type": "-sS", "ports": "22,80,443"}'
```

#### Send a Prompt to Grok with Context
```bash
python client.py grok "What are the best practices for securing a web server?" --context-type nist --context-id "800-53"
```

#### Search Documents
```bash
python client.py search "access control"
```

## API Endpoints

- `POST /execute_command`: Execute a command in the Kali container
- `POST /scan_ip_range`: Scan an IP range with multiple commands
- `POST /execute_tool`: Execute a specific security tool with customized parameters
- `POST /grok/prompt`: Send a prompt to Grok with optional context
- `POST /documents/search`: Search documents in the document store
- `GET /health`: Health check endpoint

## Context Types

### NIST Standards
- **800-53**: Security and Privacy Controls
- **CSF**: Cybersecurity Framework

### Kali Tools
- Common tools: nmap, metasploit, nikto, dirb, hydra, john, aircrack-ng, wireshark

### Web Search
- Dynamic web searches for additional information

## Docker Integration

The system uses Docker to run a Kali Linux container for security operations. The container is automatically created and managed by the MCP server.

## Security Considerations

- The system requires Docker to be installed and the user to have Docker permissions
- API keys for Grok should be kept secure
- Consider network isolation for the Kali container when performing security operations

## License

[Your License Information]
