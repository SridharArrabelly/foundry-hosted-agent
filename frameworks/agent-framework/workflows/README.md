# Workflows sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

Multi-step workflow where specialized agents run in sequence: slogan writer -> legal reviewer -> formatter.

## Planned features

- Sequential agent orchestration
- Illustrates handing structured output between agents
- Runs as one hosted agent from the caller's perspective

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
workflows/
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
Microsoft Agent Framework agent hosted via `agent-framework-foundry-hosting` + `agent-framework-foundry`.
