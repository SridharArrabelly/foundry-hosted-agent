# Tools sample (Agent Framework) — ✅ Seattle Hotel Agent

A Microsoft Agent Framework agent with a **local Python tool** (`get_available_hotels`)
that finds hotels in Seattle. Hosted via
[`agent-framework-foundry-hosting`](https://pypi.org/project/agent-framework-foundry-hosting/)
+ [`agent-framework-foundry`](https://pypi.org/project/agent-framework-foundry/) using the
**Responses** protocol.

This sample demonstrates a key advantage of code-based hosted agents over
prompt agents: **you can run arbitrary Python as an agent tool** — perfect for
private APIs, database lookups, or any custom server-side logic.

## The tool

`get_available_hotels(check_in_date, check_out_date, max_price=500)` — searches
a simulated Seattle hotel catalog and returns matching hotels with pricing and
ratings. Simulates a call to a fake hotel-availability API.

## Layout

```
tools/
├── README.md          ← you are here
├── main.py            ← agent + tool + AgentServer entry point
├── agent.yaml         ← Foundry hosted agent manifest (name: agent-framework-tools)
├── Dockerfile
├── .dockerignore
├── pyproject.toml     ← uv-managed deps
├── uv.lock
├── .env.example
└── .vscode/           ← F5 debugging with the Agent Inspector
```

## Prerequisites

- Microsoft Foundry project with a chat model deployed (e.g. `gpt-4o-mini`).
  Note your project endpoint URL and model deployment name.
- Azure CLI — `az login` and verify with `az account show`.
- Python 3.10+ (`python --version`).

## Environment variables

Copy `.env.example` to `.env` and fill in:

```
FOUNDRY_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

Or set them in PowerShell:

```powershell
$env:FOUNDRY_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
$env:AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

## Running locally

Open **this folder** (`frameworks/agent-framework/tools/`) as the VS Code
workspace root so the `.vscode/` configs resolve correctly.

### Set up the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Or with `uv`:

```powershell
uv sync
```

### Option 1: F5 in VS Code (recommended)

Press **F5** in VS Code. This runs `Debug Local Workflow HTTP Server`, which:

1. Starts the HTTP server with `debugpy` attached on port 5679.
2. Serves the agent on `http://localhost:8088/`.
3. Opens the AI Toolkit **Agent Inspector** for interactive testing.

### Option 2: Terminal

```powershell
python main.py
```

The agent listens on `http://localhost:8088/`.

## Testing the agent

**PowerShell:**

```powershell
$body = @{
    input  = "I need a hotel in Seattle from 2025-03-15 to 2025-03-18, budget under `$200 per night"
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8088/responses -Method Post -Body $body -ContentType "application/json"
```

**curl (bash / Git Bash):**

```bash
curl -sS -H "Content-Type: application/json" -X POST http://localhost:8088/responses \
    -d '{"input":"Find me hotels in Seattle for March 20-23, 2025 under $200 per night","stream":false}'
```

The agent invokes `get_available_hotels` and returns a formatted list.

## Deploying to Microsoft Foundry

1. Open **this folder** in VS Code.
2. Command Palette → `Microsoft Foundry: Deploy Hosted Agent`.
3. Follow the interactive prompts. The extension will:
   - Locate or generate a Dockerfile (this sample ships one).
   - Create / reuse an Azure Container Registry for the target project.
   - Build and push the image (packaging respects `.dockerignore`).
   - Create a hosted agent version using the built image. Any `.env` file at
     the folder root is parsed and its keys become the agent's environment
     variables.
   - Start the agent container on the project's capability host.
4. After deployment the agent appears under **Hosted Agents (Preview)** in the
   Microsoft Foundry extension tree. Click it to test in the integrated
   playground.

### Managed identity (MSI) permissions

Foundry runs your agent under the project's managed identity. Grant it the
built-in [**Azure AI User**](https://aka.ms/foundry-ext-project-role) role on
the Foundry project:

1. Azure Portal → your Foundry Project → **Access control (IAM)**.
2. **Add** → **Add role assignment**.
3. Role: **Azure AI User** → **Next**.
4. Assign access to: **Managed identity** → **Select members** → find the
   identity for your Foundry Project.
5. **Review + assign**. Allow a few minutes for propagation.

## References

- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [`agent-framework-foundry-hosting`](https://pypi.org/project/agent-framework-foundry-hosting/)
- [`agent-framework-foundry`](https://pypi.org/project/agent-framework-foundry/)
- [Managed Identities for Azure Resources](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/)
