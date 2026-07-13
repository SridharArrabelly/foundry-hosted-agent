# Basic sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

Multi-turn conversation with response tracking. The Foundry platform manages history, streaming, and background execution.

## Planned features

- Multi-turn conversation state
- Response-tracking via the Responses protocol
- No custom tools \u2014 pure model chat

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
basic/
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
