# -*- coding: utf-8 -*-
"""
MCP Server Implementation - LangGraph/LangChain Pattern
Core MCP server following tool-based architecture
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from tools import AVAILABLE_TOOLS, get_all_tool_schemas, execute_tool

class MCPServer:
    """
    MCP Server implementation following LangGraph/LangChain patterns
    Manages tool registry, execution, and streaming capabilities
    """
    
    def __init__(self):
        self.tools = AVAILABLE_TOOLS
        self.sessions = {}
        self.execution_history = []
        self.server_stats = {
            "start_time": datetime.now(),
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and statistics"""
        uptime = datetime.now() - self.server_stats["start_time"]
        
        return {
            "server_name": "FastAPI MCP Tool Server",
            "version": "2.0.0",
            "pattern": "LangGraph/LangChain Compatible",
            "uptime_seconds": int(uptime.total_seconds()),
            "available_tools": len(self.tools),
            "tool_names": list(self.tools.keys()),
            "statistics": self.server_stats,
            "capabilities": [
                "tool_execution",
                "sse_streaming", 
                "parameter_validation",
                "schema_introspection",
                "execution_history"
            ]
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """List all available tools with their schemas"""
        schemas = get_all_tool_schemas()
        
        return {
            "tools": schemas,
            "count": len(schemas),
            "server_info": self.get_server_info()
        }
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific tool"""
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        schema = tool.get_schema()
        
        return {
            "name": tool_name,
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
            "return_type": schema.return_type,
            "class_name": tool.__class__.__name__
        }
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters
        Tracks execution history and statistics
        """
        execution_id = f"exec_{int(datetime.now().timestamp() * 1000)}"
        start_time = datetime.now()
        
        # Create execution record
        execution_record = {
            "execution_id": execution_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "session_id": session_id,
            "start_time": start_time.isoformat(),
            "status": "running"
        }
        
        self.execution_history.append(execution_record)
        self.server_stats["total_executions"] += 1
        
        try:
            # Validate tool exists
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Execute the tool
            result = execute_tool(tool_name, parameters)
            
            # Update execution record
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution_record.update({
                "status": "completed",
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "result": result
            })
            
            self.server_stats["successful_executions"] += 1
            
            return {
                "execution_id": execution_id,
                "status": "success",
                "tool_name": tool_name,
                "input_parameters": parameters,
                "output": result,
                "execution_time_seconds": execution_time,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            # Update execution record with error
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution_record.update({
                "status": "failed",
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "error": str(e)
            })
            
            self.server_stats["failed_executions"] += 1
            
            return {
                "execution_id": execution_id,
                "status": "error",
                "tool_name": tool_name,
                "input_parameters": parameters,
                "error": str(e),
                "execution_time_seconds": execution_time,
                "timestamp": end_time.isoformat()
            }
    
    async def execute_tool_stream(self, tool_name: str, parameters: Dict[str, Any], session_id: Optional[str] = None):
        """
        Execute a tool with streaming response
        Yields execution events as they occur
        """
        execution_id = f"stream_exec_{int(datetime.now().timestamp() * 1000)}"
        
        # Yield start event
        yield {
            "event": "execution_start",
            "execution_id": execution_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add small delay to simulate streaming
        await asyncio.sleep(0.1)
        
        # Yield validation event
        try:
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            yield {
                "event": "validation_success",
                "execution_id": execution_id,
                "message": "Tool and parameters validated",
                "timestamp": datetime.now().isoformat()
            }
            
            await asyncio.sleep(0.1)
            
            # Execute tool
            yield {
                "event": "execution_progress",
                "execution_id": execution_id,
                "message": f"Executing {tool_name}...",
                "timestamp": datetime.now().isoformat()
            }
            
            result = execute_tool(tool_name, parameters)
            
            # Yield result
            yield {
                "event": "execution_result",
                "execution_id": execution_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Yield completion
            yield {
                "event": "execution_complete",
                "execution_id": execution_id,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Yield error
            yield {
                "event": "execution_error",
                "execution_id": execution_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "event": "execution_complete",
                "execution_id": execution_id,
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_execution_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent execution history"""
        recent_history = self.execution_history[-limit:] if limit else self.execution_history
        
        return {
            "history": recent_history,
            "total_executions": len(self.execution_history),
            "showing": len(recent_history),
            "statistics": self.server_stats
        }
    
    def create_session(self, session_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new execution session"""
        if session_id in self.sessions:
            return {"error": f"Session '{session_id}' already exists"}
        
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "executions": [],
            "status": "active"
        }
        
        self.sessions[session_id] = session
        
        return {
            "message": f"Session '{session_id}' created successfully",
            "session": session
        }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session"""
        if session_id not in self.sessions:
            return {"error": f"Session '{session_id}' not found"}
        
        return self.sessions[session_id]
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all active sessions"""
        return {
            "sessions": list(self.sessions.values()),
            "total_sessions": len(self.sessions)
        }
    
    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a specific tool"""
        if tool_name not in self.tools:
            return {
                "valid": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            tool = self.tools[tool_name]
            validated_params = tool.validate_input(parameters)
            
            return {
                "valid": True,
                "validated_parameters": validated_params,
                "tool_name": tool_name
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "tool_name": tool_name,
                "provided_parameters": parameters
            }