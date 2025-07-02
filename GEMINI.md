# MCP Tool Server Development Guide

This file provides guidance for AI assistants working with this MCP tool server repository.

## Development Commands

### Server Management
```bash
# Start the MCP server with mock tools
source venv/bin/activate && python main.py
```

### Testing
```bash
# Run all automated tests (requires server to be running)
python test_sse.py --auto

# Run interactive test suite
python test_sse.py

# Test with Python SSE client
python client.py
```

## Architecture Overview

### Core Components

- **`main.py`**: FastAPI application with MCP server, tool execution, and SSE streaming.
- **`tools.py`**: Mock tools following LangGraph/LangChain pattern with BaseTool class.
- **`mcp_server.py`**: MCP server implementation for tool management and execution.
- **`client.py`**: Command-line client for testing SSE streams and tool endpoints.
- **`test_sse.py`**: Test suite for the application.

### Key Architectural Patterns

- **LangGraph/LangChain Tool Pattern**: Tools inherit from `BaseTool` class with schema definition and validation.
- **Mock Tools**: All tools are mocked for laboratory/testing purposes without external dependencies.
- **MCP Server**: Manages tool registry, execution history, and streaming capabilities.
- **SSE Streams**: Real-time event streams for tool execution and system metrics.

### Available Mock Tools

1. **`analyze_repository`**: Analyze GitHub repositories
2. **`resolve_library`**: Resolve library names to IDs
3. **`get_documentation`**: Retrieve library documentation
4. **`web_search`**: Mock web search functionality

### Endpoints Structure

- **SSE Streams**:
  - `/stream`: Main event stream
  - `/metrics`: System metrics stream
- **MCP Tool Endpoints**:
  - `/mcp/tools`: List all available tools
  - `/mcp/tools/{tool_name}/schema`: Get tool schema
  - `/mcp/tools/{tool_name}/execute`: Execute a tool
  - `/mcp/tools/{tool_name}/execute-stream`: Execute tool with SSE streaming
- **Health Check**:
  - `/health`: Server status and statistics

## Development Environment Setup

The server runs on `http://127.0.0.1:8000` with a web interface for testing tools and streaming. All tools are mocked for lab/testing purposes.

## Testing Strategy

The test suite is designed to work with the mock tools, ensuring reliable testing without external dependencies.

# Important Instructions

- This is a laboratory/testing MCP server with mock tools only
- All tools are fictional and for demonstration purposes
- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- NEVER proactively create documentation files unless explicitly requested