# Files sample (Agent Framework) — ⚠️ file-upload diagnostic

An Agent Framework hosted agent that reads files a user uploaded via the
Foundry Playground's **Files** pane (or the `/files` platform endpoint). Used
to reproduce and diagnose reports that "file attachments don't work" on
hosted agents.

## The correct pattern

> Files attached to a hosted agent are **not** sent inline in the `/responses`
> message. The Foundry platform stores them on the **per-session sandbox
> filesystem** (`$HOME` inside the container). The agent reads them from disk
> with normal Python file I/O.

If a client tries to push bytes inline (e.g. as `DataContent` or an OpenAI
`input_file` content item) the platform generally drops them — which is the
customer bug report we're validating here.

## What this sample does

- **Server** (`main.py`) — Agent Framework agent with two tools:
  - `list_files()` — lists files under `FILES_ROOT` (defaults to `$HOME`).
  - `read_text_file(filename)` — reads a text file (UTF-8, up to 64 KiB).
  - Agent middleware `log_incoming_middleware` logs every incoming message
    (role, content types, media types, byte sizes, text previews) so you can
    see exactly what the platform delivers.

- **Client B** (`clients/test_files_endpoint.py`) — **primary test**. Uploads
  a file via `POST /files`, then asks the agent to describe it. Mirrors what
  the Foundry Playground's Files pane does under the hood.

- **Client A** (`clients/test_datacontent.py`) — **anti-pattern demo**. Sends
  the file inline via `input_file` in `/responses`. Reproduces the customer's
  non-working approach — expected to result in "No files found" from the
  agent.

## Layout

```
files/
├── README.md
├── main.py              ← Agent with list_files + read_text_file tools
├── agent.yaml           ← name: agent-framework-files
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── .env.example
├── .vscode/
├── sandbox/             ← local FILES_ROOT (gitignored except for a placeholder)
└── clients/
    ├── sample.txt
    ├── test_datacontent.py     ← Client A - anti-pattern
    └── test_files_endpoint.py  ← Client B - correct pattern
```

## Prerequisites

- Microsoft Foundry project with a chat model deployed (e.g. `gpt-4o-mini` or `gpt-5.4-mini`).
- Azure CLI (`az login`).
- Python 3.10+.

## Run locally

Open **this folder** as the VS Code workspace root.

```powershell
copy .env.example .env
# edit .env - set PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME

uv sync
python main.py
```

Wait for `File Inspection Agent Server running on http://localhost:8088` and
the line telling you where `FILES_ROOT` is.

## Test locally

Locally the `/files` endpoint isn't exposed by the AgentServer library — the
platform provides it in Foundry. So for a local end-to-end test:

1. Drop `clients/sample.txt` into the printed `FILES_ROOT` directory
   (the sample defaults `FILES_ROOT` to `./sandbox` locally):
   ```powershell
   Copy-Item clients\sample.txt sandbox\
   ```
2. Ask the agent about it:
   ```powershell
   $body = @{
       input  = "What text files are in my session sandbox? Read sample.txt and describe it."
       stream = $false
   } | ConvertTo-Json
   Invoke-RestMethod -Uri http://localhost:8088/responses -Method Post -Body $body -ContentType "application/json"
   ```

You should see the agent call `list_files` and `read_text_file` in the server
log and describe the file's contents in the response.

## Test the anti-pattern (Client A)

```powershell
python clients/test_datacontent.py
```

Expected: the agent responds with "No files found in the session sandbox."
because inline `input_file` bytes are not persisted to disk. This failure happens when you use `DataContent` inline.

## Test end-to-end against a deployed agent

1. Deploy this folder via `Microsoft Foundry: Deploy Hosted Agent`.
2. In the Foundry Portal open the agent's Playground.
3. On the right, open the **Files** pane and upload `clients/sample.txt`. It
   lands in the session's `HOME/`.
4. In the chat, ask: "list my files and describe sample.txt". The agent
   should read and summarize the file.

Or, from code, use `clients/test_files_endpoint.py`:
```powershell
python clients/test_files_endpoint.py --url https://<your-deployed-agent-url>
```

## References

- [Hosted agents in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents) — see the "stateful workloads via `$HOME` and `/files`" note.
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
