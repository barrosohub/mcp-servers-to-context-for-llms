# 🚀 FastAPI SSE with Generic MCP Client

This project demonstrates a complete implementation of **Server-Sent Events (SSE)** using FastAPI, integrated with a **generic Model Context Protocol (MCP) client** supporting both **DeepWiki** and **Context7**.

## 📋 Features

- ✅ **FastAPI Server** with multiple SSE endpoints
- ✅ **Generic MCP Integration** for services like DeepWiki and Context7
- ✅ **Mocked Backend** for local development and testing
- ✅ **Modern and Interactive Web Interface** to test all features
- ✅ **Python Client** for consuming streams and testing MCP endpoints
- ✅ **Multiple event types**: heartbeat, notifications, metrics, sensors
- ✅ **Real-time GitHub repository analysis** via DeepWiki
- ✅ **AI-powered documentation retrieval** via Context7
- ✅ **Automated and interactive tests**

## ⚙️ Environment Setup

### 1. Running with Docker (Recommended)

**Build the Docker image:**
```bash
docker build -t fastapi-sse-app .
```

**Run the Docker container:**
```bash
docker run -d -p 8000:8000 --name sse-app fastapi-sse-app
```
The application will be accessible at `http://localhost:8000`.

### 2. Manual Setup

#### Install Dependencies
```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Run the Server
```bash
python main.py
```
By default, the server runs with **mocked MCP services**. To use the live services, you must edit `main.py` and set `USE_MOCKS = False`.

The server will start at `http://127.0.0.1:8000`.

## 🌐 Web Interface

Access `http://127.0.0.1:8000` to see the full web interface with:

- **Simultaneous connection** to multiple SSE streams
- **Interactive controls** for DeepWiki (repository analysis) and Context7 (documentation retrieval)
- **Real-time event display** and statistics

## 🐍 Python Client

Run the Python client to test the endpoints from your terminal:

```bash
python client.py
```

The client offers an interactive menu to:
1. Connect to the main SSE stream
2. Connect to the metrics stream
3. Test DeepWiki and Context7 endpoints

## 🧪 Run Tests

First, ensure the server is running: `python main.py`

### Automated Tests
```bash
python test_sse.py --auto
```

### Interactive Tests
```bash
python test_sse.py
```

The tests verify:
- ✅ Server health check
- ✅ SSE streams (main and metrics)
- ✅ MCP endpoints for DeepWiki and Context7 using the mocked server

## 📊 Available Endpoints

### SSE Streams
- **GET `/stream`**: Main event stream with messages, heartbeats, etc.
- **GET `/metrics`**: Real-time system metrics stream.

### MCP Endpoints
- **POST `/mcp/deepwiki/tools`**: List available tools for DeepWiki.
- **POST `/mcp/deepwiki/analyze`**: Analyze a repository.
  ```json
  { "repository": "microsoft/vscode" }
  ```
- **POST `/mcp/context7/tools`**: List available tools for Context7.
- **POST `/mcp/context7/docs`**: Get documentation for a library.
  ```json
  { "library": "/vercel/next.js" }
  ```

### Health Check
- **GET `/health`**: Server health check.

## 🔧 Consuming with Tools (Examples)

### cURL
```bash
# Main SSE stream
curl -N -H "Accept: text/event-stream" http://127.0.0.1:8000/stream

# Analyze a repository with DeepWiki
curl -X POST http://127.0.0.1:8000/mcp/deepwiki/analyze \
  -H "Content-Type: application/json" \
  -d '{"repository": "microsoft/vscode"}'

# Get library docs with Context7
curl -X POST http://127.0.0.1:8000/mcp/context7/docs \
  -H "Content-Type: application/json" \
  -d '{"library": "/vercel/next.js"}'

# Health check
curl http://127.0.0.1:8000/health
```

---

**Happy Coding! 🚀**
