
from typing import Dict, Any, List

def get_library_docs(library_id: str, tokens: int = 5000, topic: str = "") -> Dict[str, Any]:
    """
    Mocks the Context7 get_library_docs tool.
    Retrieves documentation for a given library ID.
    """
    print(f"Mocking get_library_docs for ID: {library_id}, tokens: {tokens}, topic: {topic}")
    # Simulate a delay
    import time
    time.sleep(0.5)
    
    mock_docs = {
        "/vercel/next.js": "Next.js is a React framework for building full-stack web applications. You can use React Components to build your UI, and Next.js for additional features and optimizations.",
        "/react/react": "React is a JavaScript library for building user interfaces. It lets you compose complex UIs from small and isolated pieces of code called 'components'.",
        "/vue/vue": "Vue.js is a progressive framework for building user interfaces. Unlike other monolithic frameworks, Vue is designed from the ground up to be incrementally adoptable."
    }
    
    docs = mock_docs.get(library_id, f"No documentation found for {library_id}. This is a mock response.")
    
    return {
        "status": "success",
        "tool_name": "get_library_docs",
        "library_id": library_id,
        "documentation": docs,
        "tokens_retrieved": min(tokens, len(docs)),
        "topic": topic if topic else "general",
        "mocked": True
    }

def resolve_library_id(library_name: str) -> Dict[str, Any]:
    """
    Mocks the Context7 resolve_library_id tool.
    Resolves a library name to a Context7-compatible library ID.
    """
    print(f"Mocking resolve_library_id for name: {library_name}")
    import time
    time.sleep(0.3)
    
    mock_resolutions = {
        "next.js": [{"library_id": "/vercel/next.js", "name": "Next.js", "description": "React framework"}],
        "react": [{"library_id": "/react/react", "name": "React", "description": "JavaScript UI library"}],
        "vue": [{"library_id": "/vue/vue", "name": "Vue.js", "description": "Progressive UI framework"}],
    }
    
    resolved_data = mock_resolutions.get(library_name.lower(), [{"library_id": f"/{library_name}/unknown", "name": library_name, "description": "Mocked unknown library"}])
    
    return {
        "status": "success",
        "tool_name": "resolve_library_id",
        "library_name": library_name,
        "resolved_ids": resolved_data,
        "mocked": True
    }

def analyze_repository(repository: str) -> Dict[str, Any]:
    """
    Mocks the DeepWiki analyze_repository tool.
    Analyzes a given GitHub repository.
    """
    print(f"Mocking analyze_repository for repo: {repository}")
    import time
    time.sleep(1.0)
    
    mock_analysis = {
        "vercel/next.js": {"lines_of_code": 500000, "languages": ["TypeScript", "JavaScript"], "stars": 120000},
        "facebook/react": {"lines_of_code": 700000, "languages": ["JavaScript", "TypeScript"], "stars": 200000},
    }
    
    analysis_data = mock_analysis.get(repository.lower(), {"lines_of_code": 10000, "languages": ["Python"], "stars": 1000})
    
    return {
        "status": "success",
        "tool_name": "analyze_repository",
        "repository": repository,
        "analysis_data": analysis_data,
        "mocked": True
    }

def list_deepwiki_tools() -> Dict[str, Any]:
    """
    Mocks the DeepWiki list_tools tool.
    Lists available DeepWiki tools.
    """
    print("Mocking list_deepwiki_tools")
    import time
    time.sleep(0.1)
    
    return {
        "status": "success",
        "tool_name": "list_deepwiki_tools",
        "tools": [
            {"name": "analyze_repository", "description": "Analyzes a GitHub repository"},
            {"name": "search_repositories", "description": "Searches for GitHub repositories"}
        ],
        "mocked": True
    }

# Define a dictionary of available tools
AVAILABLE_TOOLS = {
    "get_library_docs": get_library_docs,
    "resolve_library_id": resolve_library_id,
    "analyze_repository": analyze_repository,
    "list_deepwiki_tools": list_deepwiki_tools,
}

def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Returns the schema for a given tool, similar to LangGraph's tool definition.
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {"error": f"Tool '{tool_name}' not found."}

    tool_func = AVAILABLE_TOOLS[tool_name]
    
    # Basic schema extraction (can be expanded for more detailed parameter types)
    schema = {
        "name": tool_func.__name__,
        "description": tool_func.__doc__.strip() if tool_func.__doc__ else "",
        "parameters": {}
    }
    
    # Inspect function signature for parameters
    import inspect
    sig = inspect.signature(tool_func)
    for param_name, param in sig.parameters.items():
        if param_name == 'return': # Skip return type hint
            continue
        
        param_type = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
        default_value = param.default if param.default != inspect.Parameter.empty else None
        
        schema["parameters"][param_name] = {
            "type": param_type,
            "default": default_value,
            "required": param.default == inspect.Parameter.empty
        }
        
    return schema

def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """
    Returns schemas for all available tools.
    """
    return [get_tool_schema(name) for name in AVAILABLE_TOOLS.keys()]
