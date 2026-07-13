# Microsoft Agent Framework samples

Samples built with the [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
and hosted via the [Azure AI AgentServer SDK](https://pypi.org/project/azure-ai-agentserver-agentframework/).

## Samples in this folder

| Sample | Protocol | Status | Description |
|---|---|---|---|
| [`basic/`](basic/) | Responses | 🚧 | Multi-turn conversation with response tracking |
| [`tools/`](tools/) | Responses | ✅ | Seattle Hotel Agent — custom Python tool callable during chat |
| [`workflows/`](workflows/) | Responses | 🚧 | Slogan → legal review → formatting pipeline |
| [`caller/`](caller/) | Responses | 🚧 | Concierge that delegates to a remote specialist |
| [`executor/`](executor/) | Responses | 🚧 | Arithmetic / math expert agent |
| [`basic-invocations/`](basic-invocations/) | Invocations | 🚧 | In-memory session multi-turn conversation |
| [`mcp/`](mcp/) | Responses | 🚧 | Discovers tools from a remote MCP server |
| [`foundry-toolbox/`](foundry-toolbox/) | Responses | 🚧 | Uses centrally managed tools from a Foundry Toolbox |
| [`files/`](files/) | Responses | ⚠️ | Diagnostic - hosted agent + clients to repro file-upload / `DataContent` handling |

## Protocol reference

- **Responses** — Best for most agents; the Foundry platform manages history,
  streaming, and background execution.
- **Invocations** — Best for agents that need full HTTP control, custom
  payloads, or long-running async workflows.
- **Invocations (WebSocket)** — Best for real-time voice and bidirectional
  streaming.

See [protocol documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
for a full comparison.

## Common structure

Every sample in this folder ships the same layout:

```
<sample>/
├── README.md          ← sample-specific run + deploy instructions
├── main.py            ← agent definition and entry point
├── agent.yaml         ← Foundry hosted agent manifest
├── Dockerfile         ← container image
├── .dockerignore
├── pyproject.toml     ← Python deps (managed with uv)
├── uv.lock
├── .env.example       ← environment variables template
└── .vscode/           ← launch.json + tasks.json for F5 debugging
```

Open the **sample folder itself** in VS Code (not the repo root) so the
`.vscode/` configs resolve `${workspaceFolder}` correctly.
