# Gemini/Claude Development Guide

This file provides guidance for AI assistants working with this repository.

## Development Commands

### Server Management
```bash
# Start the server with mocked services (default)
source venv/bin/activate && python main.py

# To use live services, edit main.py and set USE_MOCKS = False
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

- **`main.py`**: A single-file FastAPI application that provides SSE streams and a generic MCP client for external AI services.
- **`client.py`**: A command-line client for testing SSE streams and MCP endpoints.
- **`test_sse.py`**: The test suite for the application.

### Key Architectural Patterns

- **Generic MCP Client**: The `MCPClient` class in `main.py` provides a reusable client for any MCP-compliant service. It handles session initialization and method calls.
- **Mocked Services**: The `MockedMCPClient` class simulates the behavior of the live services, allowing for local development and testing without relying on external dependencies. The `USE_MOCKS` flag in `main.py` controls whether to use the mocked or live services.
- **SSE Streams**: The application uses `StreamingResponse` to provide real-time event streams for general updates and system metrics.

### Endpoints Structure

- **SSE Streams**:
  - `/stream`: Main event stream.
  - `/metrics`: System metrics stream.
- **MCP Endpoints**:
  - `/mcp/deepwiki/tools`: List DeepWiki tools.
  - `/mcp/deepwiki/analyze`: Analyze a repository.
  - `/mcp/context7/tools`: List Context7 tools.
  - `/mcp/context7/docs`: Get library documentation.
- **Health Check**:
  - `/health`: Check the server status.

## Development Environment Setup

The server runs on `http://127.0.0.1:8000`. By default, it uses mocked MCP services. To connect to the live services, you must modify the `USE_MOCKS` variable in `main.py`.

## Testing Strategy

The test suite (`test_sse.py`) is designed to run against the server with mocked services enabled. This ensures that the tests are reliable and independent of external factors.
