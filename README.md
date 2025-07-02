# MCP Server to Provide Context for LLMs

```json
{
  "mcp": {
    "servers": {
      "context7": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"]
      },
      "deepwiki": {
        "url": "https://mcp.deepwiki.com/mcp"
      }
    }
  }
}
```

This configuration sets up an MCP server that can be used to provide context for large language models (LLMs). The `context7` server uses the `@upstash/context7-mcp` package, which is a tool for managing and providing context to LLMs. The `deepwiki` server connects to an external service that provides additional context.