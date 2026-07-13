# Foundry Hosted Agent Samples

A collection of hosted agent samples for **Microsoft Foundry**, organized by
**framework** and **sample scenario** — mirroring the "Create Hosted Agent from
Sample" experience in the Microsoft Foundry VS Code extension.

Each sample is a self-contained project that you can:

- Run locally as an HTTP server
- Debug in VS Code with the AI Toolkit Agent Inspector
- Deploy to a Microsoft Foundry project as a hosted agent

> **Status legend:** ✅ implemented · ⚠️ diagnostic / in progress · 🚧 planned · — not applicable

## Framework × Sample matrix

| Sample | Description | Agent Framework | Copilot SDK | Bring Your Own | LangGraph |
|---|---|---|---|---|---|
| **Basic** (Responses) | Multi-turn conversation with response tracking | 🚧 | 🚧 | 🚧 | 🚧 |
| **Tools** (Responses) | Custom tools (e.g. hotel lookup) callable during a conversation | [✅](frameworks/agent-framework/tools/) | 🚧 | 🚧 | 🚧 |
| **Workflows** (Responses) | Multi-step pipeline (slogan → legal review → formatting) | 🚧 | 🚧 | 🚧 | 🚧 |
| **Caller** (Responses) | Concierge delegates to a remote specialist and summarizes | 🚧 | 🚧 | 🚧 | 🚧 |
| **Executor** (Responses) | Arithmetic / math expert agent | 🚧 | 🚧 | 🚧 | 🚧 |
| **Basic** (Invocations) | In-memory session for multi-turn conversations | 🚧 | 🚧 | 🚧 | 🚧 |
| **MCP** (Responses) | Dynamically discovers tools from a remote MCP server | 🚧 | 🚧 | 🚧 | 🚧 |
| **Foundry Toolbox** (Responses) | Invokes centrally managed tools from a Foundry Toolbox | 🚧 | 🚧 | 🚧 | 🚧 |
| **Files** (Responses) | Lists, reads, and interprets files with shell + code tools | [⚠️](frameworks/agent-framework/files/) | 🚧 | 🚧 | 🚧 |

Click any ✅ cell above to jump to the sample.

## Repo layout

```
foundry-hosted-agent/
├── README.md                    ← this file
├── LICENSE
└── frameworks/
    ├── agent-framework/         ← Microsoft Agent Framework samples
    │   ├── README.md
    │   ├── basic/
    │   ├── tools/               ✅ Seattle Hotel Agent
    │   ├── workflows/
    │   ├── caller/
    │   ├── executor/
    │   ├── basic-invocations/
    │   ├── mcp/
    │   ├── foundry-toolbox/
    │   └── files/
    ├── copilot-sdk/             ← GitHub Copilot SDK samples (planned)
    ├── bring-your-own/          ← Custom / BYO framework samples (planned)
    └── langgraph/               ← LangGraph samples (planned)
```

Every sample folder contains everything it needs to run and deploy on its own:
`main.py`, `agent.yaml`, `Dockerfile`, `.dockerignore`, `pyproject.toml`,
`uv.lock`, `.env.example`, `.vscode/` and its own scoped `README.md`.

## Global prerequisites

Individual samples list their own extra requirements, but all samples need:

1. **Microsoft Foundry project** with a chat model deployed (e.g. `gpt-4o-mini`).
   Note your project endpoint and model deployment name.
2. **Azure CLI** — install and run `az login`.
3. **Python 3.10+** (samples use `uv` for dependency management).
4. **Docker Desktop** — required to build the container image at deploy time.
5. **VS Code** with the **Microsoft Foundry** and **AI Toolkit** extensions —
   used to deploy and to open the Agent Inspector for local debugging.

## How to use this repo

1. Pick a framework you want to work with (start with `agent-framework/`).
2. Pick a sample from that framework's folder.
3. Open **that sample's folder** in VS Code (not the repo root) — the sample's
   `.vscode/` launch and task configs assume it is the workspace root.
4. Follow the sample's `README.md` for local run and Foundry deployment steps.

## Adding a new sample

1. Create `frameworks/<framework>/<sample>/`.
2. Copy the layout of an existing sample (e.g. `agent-framework/tools/`) — same
   set of files, adapted for the new scenario.
3. Give `agent.yaml` a unique `name` so deployed agents don't collide in a
   Foundry project (e.g. `agent-framework-workflows`).
4. Update the matrix in this README and flip the cell to ✅.

## Additional resources

- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [Azure AI AgentServer SDK](https://pypi.org/project/azure-ai-agentserver-agentframework/)
- [Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Managed Identities for Azure Resources](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/)

## Disclaimer

Samples in this repository are provided to accelerate development of hosted
agents. Review and test all output in the context of your use case. AI responses
may be inaccurate and AI actions should be monitored with human oversight.
Learn more in the transparency documents for
[Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/agents/transparency-note)
and
[Agent Framework](https://github.com/microsoft/agent-framework/blob/main/TRANSPARENCY_FAQ.md).
