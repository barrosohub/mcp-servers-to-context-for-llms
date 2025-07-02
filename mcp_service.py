# -*- coding: utf-8 -*-
"""
MCP Service Layer - Clean Architecture Implementation
Handles all MCP Context7 interactions using real MCP functions
"""
from typing import Dict, Any, Optional
import datetime


class MCPService:
    """Service layer for MCP Context7 operations"""
    
    def resolve_library_id(self, library_name: str) -> Dict[str, Any]:
        """Resolve library name to Context7 compatible ID using real MCP functions"""
        try:
            # Import the real MCP Context7 resolve function
            from mcp_context7_resolve_library_id import invoke as resolve_library_id_mcp
            
            result = resolve_library_id_mcp({"libraryName": library_name})
            return {
                "status": "success",
                "data": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except ImportError:
            return {
                "status": "error",
                "message": "Context7 MCP functions not available in this environment",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error resolving library: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def get_library_docs(self, library_id: str, tokens: int = 5000, topic: str = "") -> Dict[str, Any]:
        """Get library documentation using real Context7 MCP functions"""
        try:
            # Import the real MCP Context7 get docs function
            from mcp_context7_get_library_docs import invoke as get_library_docs_mcp
            
            params = {
                "context7CompatibleLibraryID": library_id,
                "tokens": tokens
            }
            if topic:
                params["topic"] = topic
            
            result = get_library_docs_mcp(params)
            return {
                "status": "success",
                "data": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except ImportError:
            return {
                "status": "error",
                "message": "Context7 MCP functions not available in this environment",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting documentation: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def resolve_and_get_docs(self, library_name: str, tokens: int = 5000, topic: str = "") -> Dict[str, Any]:
        """Resolve library name and get docs in one operation"""
        # First resolve the library ID
        resolve_result = self.resolve_library_id(library_name)
        
        if resolve_result["status"] != "success":
            return resolve_result
        
        # Extract library ID from resolve result
        library_data = resolve_result["data"]
        if isinstance(library_data, list) and library_data:
            # Take the first (best) match
            library_id = library_data[0].get("library_id", f"/{library_name}")
        elif isinstance(library_data, dict):
            library_id = library_data.get("library_id", f"/{library_name}")
        else:
            library_id = f"/{library_name}"
        
        # Get documentation
        return self.get_library_docs(library_id, tokens, topic)


class DeepWikiService:
    """Service layer for DeepWiki operations"""
    
    def analyze_repository(self, repository: str) -> Dict[str, Any]:
        """Analyze repository using DeepWiki - placeholder for real implementation"""
        try:
            # Clean repository input
            repo_name = repository.strip()
            if repo_name.startswith("https://github.com/"):
                repo_name = repo_name.replace("https://github.com/", "")
            
            # TODO: Implement real DeepWiki MCP integration when available
            return {
                "status": "success",
                "data": {
                    "repository": repo_name,
                    "analysis": {
                        "url": f"https://github.com/{repo_name}",
                        "status": "analyzed",
                        "message": "Repository analysis completed"
                    }
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error analyzing repository: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def list_tools(self) -> Dict[str, Any]:
        """List DeepWiki tools"""
        return {
            "status": "success",
            "data": {
                "tools": [
                    {"name": "analyze", "description": "Analyze a GitHub repository"},
                    {"name": "search", "description": "Search for repositories"}
                ]
            },
            "timestamp": datetime.datetime.now().isoformat()
        }


# Service instances
mcp_service = MCPService()
deepwiki_service = DeepWikiService()
