# MCP sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

Agent that dynamically discovers and invokes tools from a remote GitHub Copilot MCP server.

## Planned features

- Dynamic tool discovery via Model Context Protocol
- No hard-coded tool schema
- Great for teams that centralize tools in an MCP server

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
mcp/
|-- README.md
|-- main.py
|-- agent.yaml           # protocol: responses
|-- Dockerfile
|-- .dockerignore
|-- pyproject.toml
|-- uv.lock
|-- .env.example
-- .vscode/
```

## Reference implementation

See the completed [`tools/`](../tools/) sample for the working reference of a
Microsoft Agent Framework agent hosted via the Azure AI AgentServer SDK.
