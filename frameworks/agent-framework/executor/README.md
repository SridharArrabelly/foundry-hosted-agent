# Executor sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

An expert agent that answers arithmetic and math questions. Designed to be called from the `caller` sample.

## Planned features

- Focused single-domain expert
- Deterministic tool use for arithmetic
- Referenced as the remote specialist by `caller`

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
executor/
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
