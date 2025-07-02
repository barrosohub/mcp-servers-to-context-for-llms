# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server Management
```bash
# Start the FastAPI server
python main.py

# Start with virtual environment (recommended)
source venv/bin/activate && python main.py

# Start server manually with uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Testing
```bash
# Run all automated tests
python test_sse.py --auto

# Run interactive test suite
python test_sse.py

# Test with Python SSE client
python client.py
```

### Docker Operations
```bash
# Build Docker image
docker build -t fastapi-sse-app .

# Run containerized application
docker run -d -p 8000:8000 --name sse-app fastapi-sse-app
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# For development in managed environments, use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Architecture Overview

### Core Components

**FastAPI Server (`main.py`)**
- Single-file FastAPI application with integrated HTML frontend
- Server-Sent Events (SSE) implementation using `StreamingResponse`
- DeepWiki MCP (Model Context Protocol) integration for GitHub repository analysis
- Self-contained web interface with JavaScript SSE client

**SSE Client (`client.py`)**
- Python client for consuming SSE streams
- Interactive menu system for testing different endpoints
- Custom event handlers for different event types (heartbeat, notifications, sensors)

**Test Suite (`test_sse.py`)**
- Comprehensive testing for all SSE endpoints
- Supports both automated (`--auto`) and interactive modes
- Tests health checks, streaming endpoints, and broadcast API

### Key Architectural Patterns

**SSE Stream Architecture**
- All SSE endpoints use async generators (`AsyncGenerator[str, None]`)
- Streaming functions yield formatted SSE messages: `f"data: {json.dumps(data)}\n\n"`
- Client disconnect detection with `await request.is_disconnected()`
- Event types distinguished by custom event names: `f"event: {event_type}\ndata: {data}\n\n"`

**MCP Integration Pattern**
- `DeepWikiMCPClient` class handles all MCP communication
- Session-based authentication with `mcp-session-id` headers
- JSON-RPC 2.0 protocol implementation for tool calls
- Async HTTP client using `httpx` for external MCP server communication

**Frontend Integration**
- Complete HTML/CSS/JavaScript client embedded as string template (`HTML_TEMPLATE`)
- EventSource API for SSE consumption
- Real-time event display with categorization and statistics
- Repository analysis interface for DeepWiki functionality

### SSE Endpoints Structure

**Core SSE Streams:**
- `/stream` - Main event stream (messages, heartbeat, notifications, sensors)
- `/metrics` - System metrics stream (CPU, memory, RPS, network I/O)
- `/realtime/{channel}` - Custom channel-based streams

**DeepWiki MCP Endpoints:**
- `/deepwiki/tools` - Lists available MCP tools
- `/deepwiki/search` - Repository search via MCP
- `/deepwiki/analyze` - Repository analysis via MCP
- `/deepwiki/stream/{repository}` - Streaming repository analysis

### Event Type System

The application uses a structured event type system:
- `message` - Standard data events
- `heartbeat` - Server status and resource usage
- `notification` - System alerts with severity levels
- `sensor` - Simulated IoT data
- `metrics` - Performance metrics
- `deepwiki` - MCP-related events
- `analysis` - Repository analysis results

### MCP Integration Details

**Session Management:**
- Auto-initialization of MCP sessions on first tool call
- Session ID persistence for subsequent requests
- Error handling for session failures

**Tool Calling Pattern:**
```python
result = await deepwiki_client.call_tool('analyze', {'repository': 'org/repo'})
```

**Streaming Integration:**
- MCP responses converted to SSE format for real-time display
- Error handling integrated into SSE stream

## Development Environment Setup

The server runs on `http://127.0.0.1:8000` with the following endpoints:
- Main interface: `/`
- Health check: `/health`
- SSE streams: `/stream`, `/metrics`, `/realtime/{channel}`
- MCP endpoints: `/deepwiki/*`

For development, ensure the server is running before testing with `client.py` or `test_sse.py`. The health endpoint (`/health`) is used by both testing utilities to verify server availability.

## Testing Strategy

**SSE Testing Approach:**
- Stream consumption with timeout limits
- Event counting and validation
- Connection handling and error scenarios

**MCP Testing Considerations:**
- External dependency on `https://mcp.deepwiki.com/mcp`
- Session management testing
- Error handling for MCP service unavailability

The test suite provides both automated validation and interactive exploration of all endpoints.