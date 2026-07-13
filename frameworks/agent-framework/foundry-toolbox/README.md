# Foundry Toolbox sample (Agent Framework) - 🚧 planned

> **Status:** planned - not yet implemented.

## What this sample will demonstrate

Agent that discovers and invokes centrally managed tools from a Microsoft Foundry Toolbox.

## Planned features

- Centrally governed tool catalog in Foundry
- Tools shared across many agents
- Zero code changes to add or update tools \u2014 managed in Foundry

## Planned layout

When implemented, this folder will follow the standard sample layout described
in [../README.md](../README.md#common-structure):

```
foundry-toolbox/
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
