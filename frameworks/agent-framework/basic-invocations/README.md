# Basic (Invocations) sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

Multi-turn conversation using the Invocations protocol with in-memory session management.

## Planned features

- Full HTTP control over request/response payloads
- In-memory session state for multi-turn chat
- Better fit than Responses when you need custom payloads or long async workflows

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
basic-invocations/
|-- README.md
|-- main.py
|-- agent.yaml           # protocol: invocations
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
