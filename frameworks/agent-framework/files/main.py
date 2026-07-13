"""
File Inspection Agent - Agent Framework hosted agent that lists and reads files
from the per-session sandbox filesystem.

Background: on a Foundry hosted agent, files attached in the Playground
(or uploaded via the ``/files`` platform endpoint) are placed on the
per-session sandbox filesystem under ``$HOME``. The agent then reads them
from disk with normal Python file I/O - files are NOT delivered inline in
the ``/responses`` request.

This sample follows that correct pattern:
- The agent exposes two tools: ``list_files`` and ``read_text_file``.
- Both are scoped to ``FILES_ROOT`` (default ``$HOME``, fallback ``./sandbox``).
- Verbose logging via an agent middleware records the incoming user message
  so you can confirm what shape the platform actually sends to your code.
"""

import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv

load_dotenv(override=True)

from agent_framework import Agent, AgentContext
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential

# --- Verbose logging so we can see what arrives on the wire ------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logging.getLogger("agent_framework").setLevel(logging.DEBUG)
logging.getLogger("agent_framework_foundry_hosting").setLevel(logging.DEBUG)

log = logging.getLogger("files-agent")

# --- Foundry / runtime configuration -----------------------------------------
# FOUNDRY_PROJECT_ENDPOINT is auto-injected by the hosting platform at runtime;
# locally it comes from .env. Model name arrives under either spelling.

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = (
    os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    or os.environ.get("MODEL_DEPLOYMENT_NAME")
    or "gpt-4o-mini"
)

# Directory the tools are scoped to. On Foundry hosted agents this is $HOME
# (the per-session sandbox). Locally we default to ./sandbox to avoid walking
# the developer's home directory.
FILES_ROOT = Path(
    os.getenv("FILES_ROOT")
    or os.getenv("HOME")
    or str(Path(__file__).parent / "sandbox")
).resolve()
FILES_ROOT.mkdir(parents=True, exist_ok=True)
log.info("FILES_ROOT = %s", FILES_ROOT)

MAX_READ_BYTES = 64 * 1024  # cap per read so we don't dump huge files to the model


INSTRUCTIONS = f"""You are a File Inspection agent running on a Foundry Hosted Agent.

Files that a user uploads to this hosted agent are placed on the per-session
sandbox filesystem at {FILES_ROOT}. To answer questions about attached files
you MUST use your tools:

- ``list_files`` to see what files are available.
- ``read_text_file`` to read the contents of a specific file.

When a user asks about their attachment or uploaded file:
1. Call ``list_files`` first.
2. Read the relevant file with ``read_text_file``.
3. Report media type (inferred from extension), byte size, and either the
   contents (if short) or the first 500 characters (if long).

If ``list_files`` returns no files, respond exactly:
"No files found in the session sandbox."

Do not invent file contents. Never claim a file exists that ``list_files`` did
not report.
"""

# --- Tools -------------------------------------------------------------------


def _safe_child(root: Path, name: str) -> Path | None:
    """Return an absolute path under ``root`` for ``name``, or None if it escapes."""
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def list_files() -> str:
    """List files available in the current session's sandbox filesystem."""
    entries = []
    for p in sorted(FILES_ROOT.rglob("*")):
        if p.is_file():
            rel = p.relative_to(FILES_ROOT).as_posix()
            entries.append(f"{rel}  ({p.stat().st_size} bytes)")
    if not entries:
        return "No files found."
    return "Files:\n" + "\n".join(entries)


def read_text_file(
    filename: Annotated[str, "Path relative to the session sandbox, e.g. 'notes.txt'"],
) -> str:
    """Read the contents of a text file from the session sandbox. Returns up to 64 KiB."""
    target = _safe_child(FILES_ROOT, filename)
    if target is None:
        return f"Error: '{filename}' escapes the sandbox."
    if not target.is_file():
        return f"Error: '{filename}' not found under {FILES_ROOT}."
    data = target.read_bytes()[:MAX_READ_BYTES]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return (
            f"'{filename}' is not UTF-8 decodable ({target.stat().st_size} bytes, "
            "likely a binary file)."
        )
    truncated = "\n\n[...truncated...]" if target.stat().st_size > MAX_READ_BYTES else ""
    return f"--- {filename} ({target.stat().st_size} bytes) ---\n{text}{truncated}"


# --- Middleware --------------------------------------------------------------


async def log_incoming_middleware(
    context: AgentContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    """Log the shape of every incoming request so we can diagnose wire behavior."""
    log.info("---- incoming request ----")
    log.info("Number of messages in context: %d", len(context.messages))
    for i, m in enumerate(context.messages):
        log.info("  messages[%d].role=%s  #contents=%d", i, m.role, len(m.contents))
        for j, c in enumerate(m.contents):
            summary = f"type={type(c).__name__}"
            media_type = getattr(c, "media_type", None)
            if media_type:
                summary += f" media_type={media_type}"
            data = getattr(c, "data", None)
            if data is not None:
                summary += f" data_len={len(data) if hasattr(data, '__len__') else 'n/a'}"
            text = getattr(c, "text", None)
            if text is not None:
                summary += f" text={text[:80]!r}"
            log.info("    contents[%d]: %s", j, summary)
    await call_next()


# --- Entry point -------------------------------------------------------------


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT_NAME,
        credential=DefaultAzureCredential(),
    )

    agent = Agent(
        client=client,
        name="FileInspectionAgent",
        instructions=INSTRUCTIONS,
        tools=[list_files, read_text_file],
        middleware=[log_incoming_middleware],
        # The hosting platform manages conversation history; don't double-store it.
        default_options={"store": False},
    )

    print(f"File Inspection Agent Server running on http://localhost:8088")
    print(f"Sandbox directory: {FILES_ROOT}")
    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
