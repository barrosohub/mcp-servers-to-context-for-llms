# -*- coding: utf-8 -*-
"""
FastAPI MCP Server - LangGraph/LangChain Tool Pattern POC
MCP server with exposed tools and SSE streaming
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, AsyncGenerator, List
import uvicorn
import json
import asyncio
import time
from datetime import datetime

from tools import AVAILABLE_TOOLS, get_tool_schema, get_all_tool_schemas, execute_tool
from mcp_server import MCPServer

# App configuration
app = FastAPI(
    title="FastAPI MCP Tool Server", 
    version="2.0.0",
    description="POC MCP server with LangGraph/LangChain tool pattern and SSE streaming"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Server
mcp_server = MCPServer()

# SSE Event Generator
async def generate_sse_events(event_type: str = "general") -> AsyncGenerator[str, None]:
    """Generate SSE events for streaming"""
    counter = 0
    while True:
        counter += 1
        timestamp = datetime.now().isoformat()
        
        if event_type == "metrics":
            data = {
                "timestamp": timestamp,
                "event": "metrics",
                "data": {
                    "cpu_usage": 45.2 + (counter % 20),
                    "memory_usage": 62.8 + (counter % 15),
                    "active_connections": counter % 10,
                    "requests_count": counter
                }
            }
        else:
            data = {
                "timestamp": timestamp,
                "event": "server_status",
                "data": {
                    "status": "running",
                    "uptime": counter * 2,
                    "message": f"Server tick #{counter}"
                }
            }
        
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(2)

# UI Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Tool Server</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 1200px; margin: 0 auto; background: white; 
            padding: 30px; border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin-bottom: 10px; }
        .header p { color: #666; }
        .section { margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .section h3 { margin-bottom: 15px; color: #333; }
        .controls { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; margin-bottom: 20px; 
        }
        .control-group { padding: 15px; background: white; border-radius: 8px; }
        input, select, textarea { 
            width: 100%; padding: 10px; margin: 8px 0; 
            border: 1px solid #ddd; border-radius: 4px; font-size: 14px;
        }
        button { 
            padding: 10px 20px; margin: 5px; border: none; 
            border-radius: 4px; cursor: pointer; font-weight: 600;
            transition: background 0.2s;
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-primary:hover { background: #0056b3; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #545b62; }
        .results { 
            background: #1a1a1a; border-radius: 8px; padding: 20px;
            min-height: 200px; max-height: 400px; overflow-y: auto; 
            color: #f8f9fa; font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;
        }
        .result { 
            background: #2d2d2d; padding: 15px; margin: 10px 0; 
            border-radius: 4px; border-left: 4px solid #007bff;
        }
        .result.error { border-left-color: #dc3545; }
        .result.success { border-left-color: #28a745; }
        .result.stream { border-left-color: #17a2b8; }
        .result-header { 
            display: flex; justify-content: space-between; 
            margin-bottom: 10px; font-weight: bold;
        }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .sse-status { padding: 10px; background: #e9ecef; border-radius: 4px; margin: 10px 0; }
        .sse-status.connected { background: #d4edda; }
        .sse-status.disconnected { background: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ MCP Tool Server</h1>
            <p>LangGraph/LangChain Pattern POC with SSE Streaming</p>
        </div>
        
        <div class="section">
            <h3>🔧 Tool Management</h3>
            <div class="controls">
                <div class="control-group">
                    <h4>Available Tools</h4>
                    <button class="btn-secondary" onclick="listTools()">List All Tools</button>
                    <select id="toolSelect" onchange="loadToolSchema()">
                        <option value="">Select a tool...</option>
                    </select>
                </div>
                <div class="control-group">
                    <h4>Tool Execution</h4>
                    <textarea id="toolParams" placeholder="Tool parameters (JSON)" rows="3"></textarea>
                    <button class="btn-primary" onclick="executeTool()">Execute Tool</button>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>📡 SSE Streaming</h3>
            <div class="controls">
                <div class="control-group">
                    <div class="sse-status disconnected" id="sseStatus">Disconnected</div>
                    <button class="btn-primary" onclick="connectSSE()">Connect Stream</button>
                    <button class="btn-secondary" onclick="disconnectSSE()">Disconnect</button>
                    <button class="btn-secondary" onclick="connectMetrics()">Metrics Stream</button>
                </div>
                <div class="control-group">
                    <h4>Controls</h4>
                    <button class="btn-secondary" onclick="clearResults()">Clear Results</button>
                    <button class="btn-secondary" onclick="checkHealth()">Health Check</button>
                </div>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="result">
                <div class="result-header">
                    <span>🚀 MCP SERVER READY</span>
                    <span id="initTime"></span>
                </div>
                <div>MCP Tool Server initialized. Ready to execute tools and stream events.</div>
            </div>
        </div>
    </div>

    <script>
        let eventSource = null;
        
        document.getElementById('initTime').textContent = new Date().toLocaleTimeString();
        
        function addResult(type, title, data) {
            const results = document.getElementById('results');
            const result = document.createElement('div');
            result.className = `result ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'stream' ? '📡' : 'ℹ️';
            
            let displayData = '';
            try {
                displayData = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
            } catch {
                displayData = String(data);
            }
            
            result.innerHTML = `
                <div class="result-header">
                    <span>${icon} ${title}</span>
                    <span>${timestamp}</span>
                </div>
                <pre>${displayData}</pre>
            `;
            
            results.insertBefore(result, results.firstChild);
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = `
                <div class="result">
                    <div class="result-header">
                        <span>🧹 CLEARED</span>
                        <span>${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div>Results cleared.</div>
                </div>
            `;
        }
        
        async function apiCall(endpoint, method = 'GET', payload = null, title = '') {
            try {
                const options = {
                    method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (payload) options.body = JSON.stringify(payload);
                
                const response = await fetch(endpoint, options);
                const result = await response.json();
                
                if (response.ok) {
                    addResult('success', title, result);
                } else {
                    addResult('error', title, result.detail || 'Unknown error');
                }
                return result;
            } catch (error) {
                addResult('error', title, `Network error: ${error.message}`);
                return null;
            }
        }
        
        async function listTools() {
            const result = await apiCall('/mcp/tools', 'GET', null, 'LIST TOOLS');
            if (result && result.tools) {
                const select = document.getElementById('toolSelect');
                select.innerHTML = '<option value="">Select a tool...</option>';
                result.tools.forEach(tool => {
                    const option = document.createElement('option');
                    option.value = tool.name;
                    option.textContent = `${tool.name} - ${tool.description}`;
                    select.appendChild(option);
                });
            }
        }
        
        async function loadToolSchema() {
            const toolName = document.getElementById('toolSelect').value;
            if (!toolName) return;
            
            const result = await apiCall(`/mcp/tools/${toolName}/schema`, 'GET', null, 'TOOL SCHEMA');
            if (result && result.parameters) {
                const params = {};
                Object.keys(result.parameters).forEach(key => {
                    const param = result.parameters[key];
                    params[key] = param.default !== null ? param.default : `<${param.type}>`;
                });
                document.getElementById('toolParams').value = JSON.stringify(params, null, 2);
            }
        }
        
        async function executeTool() {
            const toolName = document.getElementById('toolSelect').value;
            const paramsText = document.getElementById('toolParams').value;
            
            if (!toolName) {
                addResult('error', 'EXECUTE TOOL', 'Please select a tool');
                return;
            }
            
            let params = {};
            if (paramsText.trim()) {
                try {
                    params = JSON.parse(paramsText);
                } catch (e) {
                    addResult('error', 'EXECUTE TOOL', 'Invalid JSON parameters');
                    return;
                }
            }
            
            await apiCall(`/mcp/tools/${toolName}/execute`, 'POST', params, `EXECUTE ${toolName.toUpperCase()}`);
        }
        
        function connectSSE() {
            if (eventSource) {
                eventSource.close();
            }
            
            eventSource = new EventSource('/stream');
            document.getElementById('sseStatus').textContent = 'Connecting...';
            
            eventSource.onopen = function() {
                document.getElementById('sseStatus').textContent = 'Connected';
                document.getElementById('sseStatus').className = 'sse-status connected';
                addResult('stream', 'SSE CONNECTED', 'Event stream connected');
            };
            
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    addResult('stream', 'SSE EVENT', data);
                } catch (e) {
                    addResult('stream', 'SSE EVENT', event.data);
                }
            };
            
            eventSource.onerror = function() {
                document.getElementById('sseStatus').textContent = 'Connection Error';
                document.getElementById('sseStatus').className = 'sse-status disconnected';
                addResult('error', 'SSE ERROR', 'Event stream connection failed');
            };
        }
        
        function connectMetrics() {
            if (eventSource) {
                eventSource.close();
            }
            
            eventSource = new EventSource('/metrics');
            document.getElementById('sseStatus').textContent = 'Connected (Metrics)';
            document.getElementById('sseStatus').className = 'sse-status connected';
            
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    addResult('stream', 'METRICS', data);
                } catch (e) {
                    addResult('stream', 'METRICS', event.data);
                }
            };
        }
        
        function disconnectSSE() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            document.getElementById('sseStatus').textContent = 'Disconnected';
            document.getElementById('sseStatus').className = 'sse-status disconnected';
            addResult('stream', 'SSE DISCONNECTED', 'Event stream disconnected');
        }
        
        async function checkHealth() {
            await apiCall('/health', 'GET', null, 'HEALTH CHECK');
        }
        
        // Auto-load tools on page load
        window.onload = function() {
            listTools();
        };
        
        // Cleanup on page unload
        window.onbeforeunload = function() {
            if (eventSource) {
                eventSource.close();
            }
        };
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
def get_home():
    """Main interface"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "FastAPI MCP Tool Server",
        "version": "2.0.0",
        "tools_available": len(AVAILABLE_TOOLS),
        "timestamp": datetime.now().isoformat()
    }

# SSE Streaming Endpoints
@app.get("/stream")
def get_event_stream():
    """General SSE event stream"""
    return StreamingResponse(
        generate_sse_events("general"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/metrics")
def get_metrics_stream():
    """Metrics SSE event stream"""
    return StreamingResponse(
        generate_sse_events("metrics"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

# MCP Tool Endpoints
@app.get("/mcp/tools")
def list_mcp_tools():
    """List all available MCP tools"""
    schemas = get_all_tool_schemas()
    return {
        "status": "success",
        "tools": schemas,
        "count": len(schemas),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/mcp/tools/{tool_name}/schema")
def get_mcp_tool_schema(tool_name: str):
    """Get schema for a specific tool"""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    schema = get_tool_schema(tool_name)
    return {
        "status": "success",
        "tool_name": tool_name,
        **schema,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/mcp/tools/{tool_name}/execute")
def execute_mcp_tool(tool_name: str, request_data: Dict[str, Any]):
    """Execute a specific MCP tool"""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        result = execute_tool(tool_name, request_data)
        return {
            "status": "success",
            "tool_name": tool_name,
            "input": request_data,
            "output": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "tool_name": tool_name,
            "error": str(e),
            "input": request_data,
            "timestamp": datetime.now().isoformat()
        }

# Tool execution with SSE streaming
@app.post("/mcp/tools/{tool_name}/execute-stream")
async def execute_mcp_tool_stream(tool_name: str, request_data: Dict[str, Any]):
    """Execute a tool with SSE streaming response"""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    async def stream_tool_execution():
        # Send start event
        start_event = {
            "event": "tool_start",
            "tool_name": tool_name,
            "input": request_data,
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(start_event)}\n\n"
        
        # Execute tool
        try:
            result = execute_tool(tool_name, request_data)
            
            # Send result event
            result_event = {
                "event": "tool_result",
                "tool_name": tool_name,
                "output": result,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(result_event)}\n\n"
            
        except Exception as e:
            # Send error event
            error_event = {
                "event": "tool_error",
                "tool_name": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
        
        # Send completion event
        completion_event = {
            "event": "tool_complete",
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(completion_event)}\n\n"
    
    return StreamingResponse(
        stream_tool_execution(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    print("🛠️  FastAPI MCP Tool Server v2.0 starting...")
    print("📡 SSE Streaming enabled")
    print("🔧 LangGraph/LangChain tool pattern")
    print("🌐 Interface: http://127.0.0.1:8000")
    print("❤️  Health: http://127.0.0.1:8000/health")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )