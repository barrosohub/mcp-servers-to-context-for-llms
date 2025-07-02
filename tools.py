# -*- coding: utf-8 -*-
"""
Mock Tools for MCP Server - LangGraph/LangChain Pattern
Tools following the LangGraph/LangChain tool definition pattern
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import inspect
import time
import json

@dataclass
class ToolParameter:
    """Tool parameter definition following LangGraph pattern"""
    name: str
    param_type: str
    description: str
    required: bool = True
    default: Any = None

@dataclass  
class ToolSchema:
    """Tool schema definition following LangGraph pattern"""
    name: str
    description: str
    parameters: List[ToolParameter]
    return_type: str = "Dict[str, Any]"

class BaseTool(ABC):
    """Base class for tools following LangGraph pattern"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool"""
        pass
    
    def get_schema(self) -> ToolSchema:
        """Get tool schema"""
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
    
    def validate_input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        validated = {}
        
        for param in self.parameters:
            if param.name in params:
                validated[param.name] = params[param.name]
            elif param.required and param.default is None:
                raise ValueError(f"Required parameter '{param.name}' is missing")
            elif param.default is not None:
                validated[param.name] = param.default
        
        return validated

class RepositoryAnalyzerTool(BaseTool):
    """Repository analysis tool"""
    
    @property
    def name(self) -> str:
        return "analyze_repository"
    
    @property
    def description(self) -> str:
        return "Analyze a GitHub repository and extract insights"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="repository",
                param_type="str",
                description="GitHub repository name in format 'owner/repo'",
                required=True
            ),
            ToolParameter(
                name="include_metrics",
                param_type="bool", 
                description="Include detailed code metrics",
                required=False,
                default=True
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute repository analysis"""
        params = self.validate_input(kwargs)
        repository = params["repository"]
        include_metrics = params.get("include_metrics", True)
        
        # Simulate processing time
        time.sleep(1.0)
        
        mock_analyses = {
            "vercel/next.js": {
                "lines_of_code": 520000,
                "languages": ["TypeScript", "JavaScript", "CSS"],  
                "stars": 125000,
                "forks": 25000,
                "contributors": 1500,
                "main_topics": ["react", "frontend", "fullstack", "ssr"],
                "complexity_score": 8.5,
                "documentation_quality": 9.2
            },
            "facebook/react": {
                "lines_of_code": 680000,
                "languages": ["JavaScript", "TypeScript", "C++"],
                "stars": 230000,
                "forks": 48000, 
                "contributors": 1800,
                "main_topics": ["ui", "library", "components", "virtual-dom"],
                "complexity_score": 9.1,
                "documentation_quality": 8.8
            },
            "microsoft/vscode": {
                "lines_of_code": 1200000,
                "languages": ["TypeScript", "JavaScript", "CSS", "Python"],
                "stars": 165000,
                "forks": 29000,
                "contributors": 2100,
                "main_topics": ["editor", "ide", "development", "extensions"],
                "complexity_score": 9.5,
                "documentation_quality": 9.0
            }
        }
        
        analysis = mock_analyses.get(
            repository.lower(),
            {
                "lines_of_code": 15000,
                "languages": ["Python", "JavaScript"],
                "stars": 1200,
                "forks": 150,
                "contributors": 25,
                "main_topics": ["utility", "tool"],
                "complexity_score": 6.0,
                "documentation_quality": 7.0
            }
        )
        
        result = {
            "tool_name": self.name,
            "repository": repository,
            "analysis": analysis,
            "timestamp": time.time(),
            "success": True
        }
        
        if not include_metrics:
            # Remove detailed metrics if not requested
            result["analysis"] = {
                "languages": analysis["languages"],
                "stars": analysis["stars"],
                "main_topics": analysis["main_topics"]
            }
        
        return result

class LibraryResolverTool(BaseTool):
    """Library ID resolution tool"""
    
    @property
    def name(self) -> str:
        return "resolve_library"
    
    @property
    def description(self) -> str:
        return "Resolve library name to compatible library ID"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="library_name",
                param_type="str", 
                description="Name of the library to resolve",
                required=True
            ),
            ToolParameter(
                name="include_alternatives",
                param_type="bool",
                description="Include alternative/similar libraries",
                required=False,
                default=False
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute library resolution"""
        params = self.validate_input(kwargs)
        library_name = params["library_name"]
        include_alternatives = params.get("include_alternatives", False)
        
        time.sleep(0.3)
        
        mock_resolutions = {
            "next.js": [
                {"library_id": "/vercel/next.js", "name": "Next.js", "description": "React framework for production", "trust_score": 9.5}
            ],
            "react": [
                {"library_id": "/facebook/react", "name": "React", "description": "JavaScript library for building UIs", "trust_score": 9.8}
            ],
            "vue": [
                {"library_id": "/vuejs/vue", "name": "Vue.js", "description": "Progressive JavaScript framework", "trust_score": 9.2}
            ],
            "fastapi": [
                {"library_id": "/tiangolo/fastapi", "name": "FastAPI", "description": "Modern Python web framework", "trust_score": 9.0}
            ],
            "express": [
                {"library_id": "/expressjs/express", "name": "Express.js", "description": "Fast Node.js web framework", "trust_score": 8.8}
            ]
        }
        
        alternatives_map = {
            "react": [
                {"library_id": "/vuejs/vue", "name": "Vue.js", "description": "Alternative frontend framework"},
                {"library_id": "/angular/angular", "name": "Angular", "description": "TypeScript-based framework"}
            ],
            "vue": [
                {"library_id": "/facebook/react", "name": "React", "description": "Popular alternative UI library"}
            ]
        }
        
        resolved = mock_resolutions.get(
            library_name.lower(),
            [{"library_id": f"/unknown/{library_name}", "name": library_name, "description": "Unknown library (mocked)", "trust_score": 5.0}]
        )
        
        result = {
            "tool_name": self.name,
            "library_name": library_name,
            "resolved_libraries": resolved,
            "count": len(resolved),
            "success": True
        }
        
        if include_alternatives and library_name.lower() in alternatives_map:
            result["alternatives"] = alternatives_map[library_name.lower()]
        
        return result

class DocumentationTool(BaseTool):
    """Library documentation retrieval tool"""
    
    @property
    def name(self) -> str:
        return "get_documentation"
    
    @property
    def description(self) -> str:
        return "Retrieve documentation for a library ID"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="library_id",
                param_type="str",
                description="Library ID (e.g., '/vercel/next.js')",
                required=True
            ),
            ToolParameter(
                name="tokens",
                param_type="int",
                description="Maximum tokens of documentation to retrieve",
                required=False,
                default=5000
            ),
            ToolParameter(
                name="topic",
                param_type="str",
                description="Specific topic to focus on",
                required=False,
                default=""
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute documentation retrieval"""
        params = self.validate_input(kwargs)
        library_id = params["library_id"]
        tokens = params.get("tokens", 5000)
        topic = params.get("topic", "")
        
        time.sleep(0.8)
        
        mock_docs = {
            "/vercel/next.js": {
                "getting_started": "Next.js is a React framework that enables server-side rendering and static site generation...",
                "routing": "Next.js has a file-system based router built on the concept of pages...",
                "api_routes": "API routes provide a solution to build your API with Next.js...",
                "deployment": "Next.js gives you the best developer experience with all the features you need for production..."
            },
            "/facebook/react": {
                "components": "Components let you split the UI into independent, reusable pieces...",
                "hooks": "Hooks let you use state and other React features without writing a class...",
                "jsx": "JSX is a syntax extension to JavaScript that describes what the UI should look like...",
                "state_management": "State lets you add interactivity to your components..."
            },
            "/tiangolo/fastapi": {
                "introduction": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+...",
                "path_parameters": "You can declare path parameters with the same syntax used by Python format strings...",
                "request_body": "When you need to send data from a client to your API, you send it as a request body...",
                "response_model": "You can declare the response model/schema in any of the path operations..."
            }
        }
        
        docs_data = mock_docs.get(library_id, {
            "general": f"Documentation for {library_id} - This is a mocked response with limited information available."
        })
        
        # Filter by topic if specified
        if topic:
            filtered_docs = {k: v for k, v in docs_data.items() if topic.lower() in k.lower()}
            if filtered_docs:
                docs_data = filtered_docs
        
        # Simulate token limiting
        full_docs = json.dumps(docs_data)
        if len(full_docs) > tokens:
            truncated_docs = full_docs[:tokens] + "... [truncated]"
            try:
                docs_data = {"content": truncated_docs}
            except:
                docs_data = {"content": full_docs[:tokens]}
        
        return {
            "tool_name": self.name,
            "library_id": library_id,
            "documentation": docs_data,
            "tokens_requested": tokens,
            "tokens_returned": min(tokens, len(full_docs)),
            "topic_filter": topic if topic else "all",
            "success": True
        }

class WebSearchTool(BaseTool):
    """Mock web search tool"""
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for information on a given query"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                param_type="str",
                description="Search query",
                required=True
            ),
            ToolParameter(
                name="max_results",
                param_type="int",
                description="Maximum number of results to return",
                required=False,
                default=5
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute web search"""
        params = self.validate_input(kwargs)
        query = params["query"]
        max_results = params.get("max_results", 5)
        
        time.sleep(0.5)
        
        # Mock search results based on query keywords
        mock_results = []
        if "python" in query.lower():
            mock_results = [
                {"title": "Python.org - Official Python Website", "url": "https://python.org", "snippet": "The official home of the Python Programming Language"},
                {"title": "Python Tutorial - W3Schools", "url": "https://w3schools.com/python", "snippet": "Learn Python programming with examples"},
            ]
        elif "javascript" in query.lower() or "js" in query.lower():
            mock_results = [
                {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/docs/Web/JavaScript", "snippet": "Comprehensive JavaScript documentation"},
                {"title": "JavaScript.info", "url": "https://javascript.info", "snippet": "Modern JavaScript tutorial"},
            ]
        elif "react" in query.lower():
            mock_results = [
                {"title": "React - A JavaScript library", "url": "https://reactjs.org", "snippet": "A JavaScript library for building user interfaces"},
                {"title": "React Documentation", "url": "https://reactjs.org/docs", "snippet": "Official React documentation"},
            ]
        else:
            mock_results = [
                {"title": f"Search results for: {query}", "url": "https://example.com", "snippet": f"Mock search result for query: {query}"},
                {"title": f"More about {query}", "url": "https://example.org", "snippet": f"Additional information about {query}"},
            ]
        
        return {
            "tool_name": self.name,
            "query": query,
            "results": mock_results[:max_results],
            "total_results": len(mock_results),
            "success": True
        }

# Tool Registry
TOOL_INSTANCES = [
    RepositoryAnalyzerTool(),
    LibraryResolverTool(), 
    DocumentationTool(),
    WebSearchTool()
]

# Create tool registry dict
AVAILABLE_TOOLS = {tool.name: tool for tool in TOOL_INSTANCES}

def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get schema for a specific tool"""
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    tool = AVAILABLE_TOOLS[tool_name]
    schema = tool.get_schema()
    
    return {
        "name": schema.name,
        "description": schema.description,
        "parameters": {
            param.name: {
                "type": param.param_type,
                "description": param.description,
                "required": param.required,
                "default": param.default
            }
            for param in schema.parameters
        },
        "return_type": schema.return_type
    }

def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """Get schemas for all available tools"""
    return [get_tool_schema(name) for name in AVAILABLE_TOOLS.keys()]

def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with given parameters"""
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    tool = AVAILABLE_TOOLS[tool_name]
    return tool.execute(**params)

def list_available_tools() -> List[str]:
    """List all available tool names"""
    return list(AVAILABLE_TOOLS.keys())

# Utility functions for compatibility
def get_library_docs(library_id: str, tokens: int = 5000, topic: str = "") -> Dict[str, Any]:
    """Legacy compatibility function"""
    return execute_tool("get_documentation", {
        "library_id": library_id,
        "tokens": tokens, 
        "topic": topic
    })

def resolve_library_id(library_name: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    return execute_tool("resolve_library", {
        "library_name": library_name
    })

def analyze_repository(repository: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    return execute_tool("analyze_repository", {
        "repository": repository
    })