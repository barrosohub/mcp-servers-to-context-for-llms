# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import datetime
import random
from typing import AsyncGenerator, Dict, Any
import uvicorn
import httpx
import uuid

app = FastAPI(
    title="FastAPI SSE Server", 
    version="1.0.0",
    description="Server-Sent Events with FastAPI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== COMPLETE HTML TEMPLATE ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI SSE Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: #333;
        }
        .controls { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .control-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #007bff;
        }
        button { 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600; 
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn-connect { background: #28a745; color: white; }
        .btn-disconnect { background: #dc3545; color: white; }
        .btn-clear { background: #6c757d; color: white; }
        button:hover { transform: translateY(-2px); opacity: 0.9; }
        .status { 
            padding: 15px; 
            border-radius: 6px; 
            font-weight: 600; 
            text-align: center; 
            margin: 10px 0;
        }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .events-container { 
            height: 400px; 
            overflow-y: auto; 
            background: #1a1a1a; 
            border-radius: 10px; 
            padding: 20px;
            font-family: 'Courier New', monospace;
        }
        .event { 
            background: #2d2d2d; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #007bff;
            color: #f8f9fa;
            font-size: 13px;
        }
        .event.heartbeat { border-left-color: #28a745; }
        .event.notification { border-left-color: #ffc107; }
        .event.sensor { border-left-color: #17a2b8; }
        .event.metrics { border-left-color: #fd7e14; }
        .event.deepwiki { border-left-color: #8a2be2; }
        .event.context7 { border-left-color: #ff69b4; }
        .event-header { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 8px; 
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FastAPI MCP Client</h1>
            <p>A demonstration of DeepWiki and Context7 integration</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <h4>🔍 DeepWiki</h4>
                <input type="text" id="repoInput" placeholder="org/repo (e.g., microsoft/vscode)" style="width:100%; padding:8px; margin:5px 0; border:1px solid #ddd; border-radius:4px;">
                <button class="btn-connect" onclick="analyzeRepo()">Analyze Repo</button>
                <button class="btn-connect" onclick="listDeepWikiTools()">List Tools</button>
            </div>

            <div class="control-group">
                <h4>📚 Context7</h4>
                <input type="text" id="libraryInput" placeholder="library (e.g., /vercel/next.js)" style="width:100%; padding:8px; margin:5px 0; border:1px solid #ddd; border-radius:4px;">
                <button class="btn-connect" onclick="getLibraryDocs()">Get Docs</button>
                <button class="btn-connect" onclick="listContext7Tools()">List Tools</button>
            </div>
            
            <div class="control-group">
                <h4>🎛️ Controls</h4>
                <button class="btn-clear" onclick="clearEvents()">Clear Events</button>
            </div>
        </div>
        
        <div class="events-container" id="eventsContainer">
            <div class="event">
                <div class="event-header">
                    <span>🚀 SYSTEM</span>
                    <span id="initialTime"></span>
                </div>
                <div>MCP client initiated. Use the controls to interact with the services.</div>
            </div>
        </div>
    </div>

    <script>
        // Initialize timestamp
        document.getElementById('initialTime').textContent = new Date().toLocaleTimeString();
        
        const eventsContainer = document.getElementById('eventsContainer');
        
        function addEvent(source, type, data) {
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const icons = {
                deepwiki: '🔍', context7: '📚', tools: '🛠️', 
                analysis: '📋', docs: '📄', error: '❌'
            };
            
            let displayData;
            try {
                const parsed = JSON.parse(data);
                displayData = JSON.stringify(parsed, null, 2);
            } catch {
                displayData = data;
            }
            
            eventDiv.innerHTML = `
                <div class="event-header">
                    <span>${icons[type] || 'ℹ️'} ${type.toUpperCase()}</span>
                    <span>${timestamp}</span>
                </div>
                <div><pre><code>${displayData}</code></pre></div>
            `;
            
            eventsContainer.insertBefore(eventDiv, eventsContainer.firstChild);
        }
        
        function clearEvents() { 
            eventsContainer.innerHTML = '<div class="event"><div class="event-header"><span>🧹 SYSTEM</span><span>' + new Date().toLocaleTimeString() + '</span></div><div>Events cleared.</div></div>'; 
        }
        
        // MCP functions
        async function callMcpService(service, endpoint, payload, eventType) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    addEvent(service, eventType, JSON.stringify(result.data, null, 2));
                } else {
                    addEvent(service, 'error', JSON.stringify(result, null, 2));
                }
            } catch (error) {
                addEvent(service, 'error', `Error calling ${service}: ${error.message}`);
            }
        }

        // DeepWiki functions
        function listDeepWikiTools() {
            callMcpService('deepwiki', '/mcp/deepwiki/tools', {}, 'tools');
        }
        
        function analyzeRepo() {
            const repository = document.getElementById('repoInput').value.trim();
            if (!repository) {
                addEvent('deepwiki', 'error', 'Please enter a repository name (e.g., microsoft/vscode)');
                return;
            }
            callMcpService('deepwiki', '/mcp/deepwiki/analyze', { repository: repository }, 'analysis');
        }

        // Context7 functions
        function listContext7Tools() {
            callMcpService('context7', '/mcp/context7/tools', {}, 'tools');
        }

        function getLibraryDocs() {
            const library = document.getElementById('libraryInput').value.trim();
            if (!library) {
                addEvent('context7', 'error', 'Please enter a library name (e.g., /vercel/next.js)');
                return;
            }
            callMcpService('context7', '/mcp/context7/docs', { library: library }, 'docs');
        }
    </script>
</body>
</html>
"""

# ==================== GENERIC MCP CLIENT ====================

class MCPClient:
    """Generic MCP Client for handling different services."""
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
        self.session_id = None
        self.client = httpx.AsyncClient()

    async def initialize_session(self) -> bool:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                "clientInfo": {"name": f"fastapi-client-{self.service_name}", "version": "1.0.0"}
            }
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            self.session_id = response.headers.get("mcp-session-id")
            if self.session_id:
                print(f"MCP session initialized for {self.service_name} with session ID: {self.session_id}")
                return True
            print(f"Error: MCP session ID not found in response for {self.service_name}")
            return False
        except httpx.HTTPStatusError as e:
            print(f"HTTP error initializing MCP session for {self.service_name}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Error initializing MCP session for {self.service_name}: {e}")
        return False

    async def call_method(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.session_id and not await self.initialize_session():
            return {"error": f"Failed to initialize session for {self.service_name}"}
        
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method, "params": params or {}}
        headers = {
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id
        }
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error calling method {method} on {self.service_name}: {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_message += f" - {error_details.get('error', {}).get('message', e.response.text)}"
            except json.JSONDecodeError:
                error_message += f" - {e.response.text}"
            print(error_message)
            return {"error": error_message}
        except Exception as e:
            print(f"Error calling method {method} on {self.service_name}: {e}")
            return {"error": f"Failed to call method {method} on {self.service_name}"}

    async def list_tools(self) -> Dict[str, Any]:
        return await self.call_method("tools/list")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await self.call_method("tools/call", {"name": tool_name, "arguments": arguments})

# ==================== SERVICE CLIENTS ====================

# Configure clients for DeepWiki and Context7
USE_MOCKS = False # Set to False to use live services

if USE_MOCKS:
    deepwiki_client = MCPClient("http://localhost:8000/mock/deepwiki", "DeepWiki")
    context7_client = MCPClient("http://localhost:8000/mock/context7", "Context7")
else:
    deepwiki_client = MCPClient("https://mcp.deepwiki.com/mcp", "DeepWiki")
    context7_client = MCPClient("https://mcp.context7.com/mcp", "Context7")

# ==================== ENDPOINTS ====================

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Main page with integrated SSE client"""
    return HTMLResponse(content=HTML_TEMPLATE)



# ==================== MCP ENDPOINTS ====================

@app.post("/mcp/{service}/tools")
async def list_mcp_tools(service: str):
    client = deepwiki_client if service == "deepwiki" else context7_client
    result = await client.list_tools()
    return {
        'status': 'success',
        'timestamp': datetime.datetime.now().isoformat(),
        'data': result
    }

@app.post("/mcp/deepwiki/analyze")
async def analyze_repository(request_data: dict):
    repository = request_data.get('repository', '')
    if not repository:
        return {'status': 'error', 'message': 'Repository is required'}
    
    result = await deepwiki_client.call_tool('analyze', {'repository': repository})
    return {
        'status': 'success',
        'timestamp': datetime.datetime.now().isoformat(),
        'data': result
    }

@app.post("/mcp/context7/docs")
async def get_library_docs(request_data: dict):
    library = request_data.get('library', '')
    if not library:
        return {'status': 'error', 'message': 'Library is required'}
    
    result = await context7_client.call_tool('get_library_docs', {'library': library})
    return {
        'status': 'success',
        'timestamp': datetime.datetime.now().isoformat(),
        'data': result
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'server': 'FastAPI SSE Server with Generic MCP',
        'version': '1.0.0',
        'services': ['DeepWiki', 'Context7']
    }

if __name__ == "__main__":
    print("🚀 FastAPI MCP Client starting...")
    print("✅ Live services enabled for DeepWiki and Context7")
    print("📱 Interface: http://127.0.0.1:8000")
    print("❤️  Health: http://127.0.0.1:8000/health")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )