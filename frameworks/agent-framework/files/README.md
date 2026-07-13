# Files sample (Agent Framework) — ✅ session sandbox files

An Agent Framework hosted agent that reads files a user uploaded via the
Foundry Portal Playground's **Files** pane (or the VS Code Agent Inspector's
Files pane). Built to explain — and prove — the correct pattern for file
attachments on Foundry hosted agents.

## The correct pattern

> Files attached to a hosted agent are **not** sent inline in the `/responses`
> message. Foundry runs each session in a **per-session micro-VM–isolated
> sandbox** with a persistent filesystem. Uploaded files land under `$HOME`
> inside that sandbox, and the agent reads them from disk with normal Python
> file I/O.

If a client tries to push bytes inline as Agent Framework `DataContent`
(or as an OpenAI `input_file` content item), the platform generally drops
them — which is the common customer bug report this sample validates.

## Two things have to be right

For the Playground Files pane to actually appear and for uploads to reach
the agent's `$HOME`:

1. **The right hosting SDK.** Use
   [`agent-framework-foundry-hosting`](https://pypi.org/project/agent-framework-foundry-hosting/)
   (this sample does). It declares session/sandbox capability so the Portal
   lights up the Files pane. The older beta
   `azure-ai-agentserver-agentframework` serves `/responses` but does not
   declare session/files, so the Portal treats the agent as stateless and no
   Files pane appears.
2. **The right protocol version in `agent.yaml`.**
   `protocols: responses: 2.0.0` — pairs with the hosting SDK above.

If either is wrong, upload from the Portal will silently no-op or the Files
pane won't be visible.

## What this sample does

- **Server** (`main.py`) — Agent Framework agent with two tools:
  - `list_files()` — lists files under `FILES_ROOT` (defaults to `$HOME`
    inside the Foundry micro-VM; falls back to `./sandbox` for local dev).
  - `read_text_file(filename)` — reads a text file (UTF-8, up to 64 KiB).
  - Agent middleware `log_incoming_middleware` logs every incoming message
    (role, content types, media types, byte sizes, text previews) so you can
    see exactly what the platform delivers.

- **Client A — anti-pattern demo** (`clients/test_datacontent.py`) — sends
  the file inline via OpenAI `input_file` (the wire equivalent of Agent
  Framework `DataContent`). Reproduces the customer's non-working approach —
  the agent should reply "No files found in the session sandbox." because
  inline bytes are never persisted to the sandbox filesystem. Sends an Entra
  bearer token automatically when the URL is `*.azure.com` / `*.azure.net`.

There is intentionally no "upload via `/files` from a script" client — the
correct programmatic path is to use the Foundry Portal Playground Files pane
(or the VS Code Agent Inspector) which handles session lifecycle and the
sandbox upload for you.

## Layout

```
files/
├── README.md
├── main.py              ← Agent with list_files + read_text_file tools
├── agent.yaml           ← name: agent-framework-files, responses: 2.0.0
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── .env.example
├── .vscode/
├── sandbox/             ← local FILES_ROOT (gitignored except for a placeholder)
└── clients/
    ├── sample.txt
    └── test_datacontent.py     ← Client A - anti-pattern demo
```

## Prerequisites

- Microsoft Foundry project with a chat model deployed (e.g. `gpt-4o-mini`).
- Azure CLI (`az login`).
- Python 3.10+.

## Run locally

Open **this folder** as the VS Code workspace root.

```powershell
copy .env.example .env
# edit .env - set FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME

uv sync
python main.py
```

Wait for the server-ready line and note where `FILES_ROOT` is printed.

## Prove the anti-pattern (Client A) locally

Make sure the sandbox is empty first — otherwise the agent will find leftover
files and produce a false positive.

```powershell
Remove-Item .\sandbox\sample.txt -ErrorAction SilentlyContinue
python clients\test_datacontent.py
```

Expected: the agent responds with **"No files found in the session sandbox."**
because inline `input_file` bytes are not persisted to disk. This is exactly
the failure that motivated this sample.

## Test end-to-end against a deployed agent

1. Deploy this folder — see [deployment note](#deployment-note) below.
2. In the Foundry Portal open the agent's Playground.
3. Send any bootstrap message (e.g. "hi"). This starts the session and unlocks
   the **Files** pane on the right.
4. In the Files pane, upload `clients/sample.txt`. It lands in the session's
   `$HOME/`.
5. In the chat, ask: "list my files and describe sample.txt". The agent
   should read and summarize the file.

The same works from VS Code with the **Microsoft Foundry: Test Hosted Agent**
command (Agent Inspector). The Agent Inspector opens a session immediately,
so the Files pane is usable without a bootstrap message.

## Prove the anti-pattern against the deployed agent

Each deployed session gets a fresh, empty sandbox, so no cleanup needed.

```powershell
python clients\test_datacontent.py --url https://<your-resource>.services.ai.azure.com/api/projects/<your-project>/agents/agent-framework-files
```

Expected: same as local — agent replies "No files found in the session
sandbox." (Auth is automatic via `DefaultAzureCredential`; make sure you're
signed in with `az login` and have the `Azure AI User` role on the project.)

## Deployment note

The Foundry VS Code extension currently uploads the **entire git repo** as
the Docker build context (not the folder you have open as workspace root).
Because this repo has multiple samples under `frameworks/`, the extension's
build fails at `COPY pyproject.toml uv.lock ./` — that file isn't at the repo
root.

**Workaround:** build and push with the Azure CLI from this folder, then
choose "Use existing image" in the extension's Deploy flow:

```powershell
az acr build `
  --registry <your-acr-name> `
  --image agent-framework-files:v1 `
  --file Dockerfile `
  .
```

## References

- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [`agent-framework-foundry-hosting`](https://pypi.org/project/agent-framework-foundry-hosting/)
- [`agent-framework-foundry`](https://pypi.org/project/agent-framework-foundry/)
- [Hosted agents in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents)
