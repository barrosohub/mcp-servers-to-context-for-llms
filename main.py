# -*- coding: utf-8 -*-
"""
FastAPI MCP Client - Clean Architecture Implementation
Real MCP Context7 integration without mocks
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, AsyncGenerator
import uvicorn
import json
import asyncio

from tools import AVAILABLE_TOOLS, get_all_tool_schemas

# App configuration
app = FastAPI(
    title="FastAPI MCP Tool Server", 
    version="1.0.0",
    description="Proof-of-concept MCP server with mocked tools and SSE"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UI Template - Simplified and Clean
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI MCP Client</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 900px; margin: 0 auto; background: white; 
            padding: 30px; border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin-bottom: 10px; }
        .header p { color: #666; }
        .controls { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }
        .control-group {
            background: #f8f9fa; padding: 20px; border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .control-group h4 { margin-bottom: 15px; color: #333; }
        input { 
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
            min-height: 300px; overflow-y: auto; color: #f8f9fa;
            font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;
        }
        .result { 
            background: #2d2d2d; padding: 15px; margin: 10px 0; 
            border-radius: 4px; border-left: 4px solid #007bff;
        }
        .result.error { border-left-color: #dc3545; }
        .result.success { border-left-color: #28a745; }
        .result-header { 
            display: flex; justify-content: space-between; 
            margin-bottom: 10px; font-weight: bold;
        }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FastAPI MCP Client</h1>
            <p>Real Context7 and DeepWiki integration</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <h4>� Context7</h4>
                <input type="text" id="libraryInput" placeholder="Library name (e.g., next.js, react, vue)">
                <button class="btn-primary" onclick="resolveLibrary()">Resolve Library</button>
                <button class="btn-primary" onclick="getLibraryDocs()">Get Documentation</button>
                <input type="text" id="libraryIdInput" placeholder="Library ID (e.g., /vercel/next.js)">
                <button class="btn-primary" onclick="getDocsById()">Get Docs by ID</button>
            </div>

            <div class="control-group">
                <h4>🔍 DeepWiki</h4>
                <input type="text" id="repoInput" placeholder="Repository (e.g., vercel/next.js)">
                <button class="btn-primary" onclick="analyzeRepo()">Analyze Repository</button>
                <button class="btn-secondary" onclick="listDeepWikiTools()">List Tools</button>
            </div>
            
            <div class="control-group">
                <h4>🛠️ Controls</h4>
                <button class="btn-secondary" onclick="clearResults()">Clear Results</button>
                <button class="btn-secondary" onclick="checkHealth()">Health Check</button>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="result">
                <div class="result-header">
                    <span>🚀 SYSTEM READY</span>
                    <span id="initTime"></span>
                </div>
                <div>MCP client initialized. Ready to interact with Context7 and DeepWiki.</div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('initTime').textContent = new Date().toLocaleTimeString();
        
        function addResult(type, title, data) {
            const results = document.getElementById('results');
            const result = document.createElement('div');
            result.className = `result ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
            
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
        
        async function apiCall(endpoint, payload, title) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                
                if (response.ok && result.status === 'success') {
                    addResult('success', title, result.data);
                } else {
                    addResult('error', title, result.message || 'Unknown error');
                }
            } catch (error) {
                addResult('error', title, `Network error: ${error.message}`);
            }
        }
        
        function resolveLibrary() {
            const library = document.getElementById('libraryInput').value.trim();
            if (!library) {
                addResult('error', 'RESOLVE LIBRARY', 'Please enter a library name');
                return;
            }
            apiCall('/mcp/context7/resolve', { library_name: library }, 'RESOLVE LIBRARY');
        }
        
        function getLibraryDocs() {
            const library = document.getElementById('libraryInput').value.trim();
            if (!library) {
                addResult('error', 'GET DOCS', 'Please enter a library name');
                return;
            }
            apiCall('/mcp/context7/docs', { library_name: library }, 'GET DOCUMENTATION');
        }
        
        function getDocsById() {
            const libraryId = document.getElementById('libraryIdInput').value.trim();
            if (!libraryId) {
                addResult('error', 'GET DOCS BY ID', 'Please enter a library ID');
                return;
            }
            apiCall('/mcp/context7/docs-by-id', { library_id: libraryId }, 'GET DOCS BY ID');
        }
        
        function analyzeRepo() {
            const repo = document.getElementById('repoInput').value.trim();
            if (!repo) {
                addResult('error', 'ANALYZE REPO', 'Please enter a repository name');
                return;
            }
            apiCall('/mcp/deepwiki/analyze', { repository: repo }, 'ANALYZE REPOSITORY');
        }
        
        function listDeepWikiTools() {
            apiCall('/mcp/deepwiki/tools', {}, 'DEEPWIKI TOOLS');
        }
        
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const result = await response.json();
                addResult('success', 'HEALTH CHECK', result);
            } catch (error) {
                addResult('error', 'HEALTH CHECK', `Error: ${error.message}`);
            }
        }
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
        "server": "FastAPI MCP Client",
        "version": "2.0.0",
        "services": ["Context7", "DeepWiki"]
    }


# Context7 Endpoints
@app.post("/mcp/context7/resolve")
def resolve_library(request_data: Dict[str, Any]):
    """Resolve library name to Context7 ID"""
    library_name = request_data.get("library_name")
    if not library_name:
        raise HTTPException(status_code=400, detail="library_name is required")
    
    return mcp_service.resolve_library_id(library_name)


@app.post("/mcp/context7/docs")
def get_library_documentation(request_data: Dict[str, Any]):
    """Get library documentation by resolving name first"""
    library_name = request_data.get("library_name")
    if not library_name:
        raise HTTPException(status_code=400, detail="library_name is required")
    
    tokens = request_data.get("tokens", 5000)
    topic = request_data.get("topic", "")
    
    return mcp_service.resolve_and_get_docs(library_name, tokens, topic)


@app.post("/mcp/context7/docs-by-id")
def get_docs_by_library_id(request_data: Dict[str, Any]):
    """Get documentation by library ID directly"""
    library_id = request_data.get("library_id")
    if not library_id:
        raise HTTPException(status_code=400, detail="library_id is required")
    
    tokens = request_data.get("tokens", 5000)
    topic = request_data.get("topic", "")
    
    return mcp_service.get_library_docs(library_id, tokens, topic)


# DeepWiki Endpoints
@app.post("/mcp/deepwiki/analyze")
def analyze_repository(request_data: Dict[str, Any]):
    """Analyze GitHub repository"""
    repository = request_data.get("repository")
    if not repository:
        raise HTTPException(status_code=400, detail="repository is required")
    
    return deepwiki_service.analyze_repository(repository)


@app.post("/mcp/deepwiki/tools")
def list_deepwiki_tools(request_data: Dict[str, Any] = None):
    """List DeepWiki tools"""
    return deepwiki_service.list_tools()


if __name__ == "__main__":
    print("🚀 FastAPI MCP Client v2.0 starting...")
    print("� Real Context7 MCP integration")
    print("� DeepWiki integration")
    print("🌐 Interface: http://127.0.0.1:8000")
    print("❤️  Health: http://127.0.0.1:8000/health")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )