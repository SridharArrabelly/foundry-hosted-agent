"""
Client B - Upload the file first via the hosted agent's ``/files`` endpoint,
then reference it in a ``/responses`` message.

Foundry hosted agents document per-session persistent storage under ``$HOME``
and a ``/files`` endpoint for stateful file persistence. This client tests
that upload path as a contrast to Client A (which pushes bytes inline).

Note: the ``/files`` endpoint is provided by the Foundry hosted-agent platform.
It may not be exposed by the local ``azure-ai-agentserver-agentframework``
server (which is the /responses server only). If the local run returns 404
for ``POST /files``, run this against a deployed hosted agent instead.

Usage:
    python clients/test_files_endpoint.py                 # local server on :8088
    python clients/test_files_endpoint.py --url <deployed>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

DEFAULT_URL = "http://localhost:8088"
SAMPLE = Path(__file__).parent / "sample.txt"


def upload(client: httpx.Client, base_url: str, path: Path, media_type: str) -> str:
    endpoint = base_url.rstrip("/") + "/files"
    print(f">>> POST {endpoint}  (uploading {path.name}, {path.stat().st_size} bytes)")
    with path.open("rb") as f:
        r = client.post(
            endpoint,
            files={"file": (path.name, f, media_type)},
            data={"purpose": "assistants"},
        )
    if r.status_code == 404:
        print(
            "!!! 404 - /files endpoint is not available on this host.\n"
            "    Try deploying the agent and running with --url <deployed-url>."
        )
        r.raise_for_status()
    r.raise_for_status()
    body = r.json()
    print(f"<<< Uploaded. Response: {json.dumps(body, indent=2)}")
    return body.get("id") or body.get("file_id") or ""


def send(client: httpx.Client, base_url: str, file_id: str) -> dict:
    endpoint = base_url.rstrip("/") + "/responses"
    payload = {
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Please describe the file I just uploaded (id above)."
                            " Include media type, size, and first 200 chars if text."
                        ),
                    },
                    {"type": "input_file", "file_id": file_id},
                ],
            }
        ],
        "stream": False,
    }
    print(f">>> POST {endpoint}  (referencing file_id={file_id!r})")
    r = client.post(endpoint, json=payload, timeout=120.0)
    r.raise_for_status()
    return r.json()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Hosted agent base URL")
    parser.add_argument("--file", default=str(SAMPLE), help="File to upload")
    parser.add_argument("--media-type", default="text/plain", help="MIME type")
    args = parser.parse_args()

    path = Path(args.file)

    with httpx.Client(timeout=120.0) as client:
        file_id = upload(client, args.url, path, args.media_type)
        if not file_id:
            print("!!! Upload succeeded but no file id returned - cannot continue.")
            return 1
        body = send(client, args.url, file_id)

    print("<<< /responses body:")
    print(json.dumps(body, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
