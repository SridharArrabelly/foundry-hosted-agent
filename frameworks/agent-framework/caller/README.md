# Caller sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

A concierge agent that delegates questions to a remote specialist agent and summarizes the answer for the user.

## Planned features

- Agent-to-agent invocation
- Summarization of remote responses
- Pairs with the `executor` sample as the remote target

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
caller/
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
