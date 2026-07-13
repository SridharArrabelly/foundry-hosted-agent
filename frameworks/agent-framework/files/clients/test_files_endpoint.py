"""
Client B - Upload the file first via the hosted agent's ``/files`` endpoint,
then reference it in a ``/responses`` message.

Foundry hosted agents document per-session persistent storage under ``$HOME``
and a ``/files`` endpoint for stateful file persistence. This client tests
that upload path as a contrast to Client A (which pushes bytes inline).

Note: the ``/files`` endpoint is provided by the Foundry hosted-agent platform.
The local agent server does NOT expose it - if the local run returns 404, run
this against a deployed hosted agent using ``--url <deployed>``.

Auth: when ``--url`` points at a Foundry endpoint (``*.services.ai.azure.com``
or ``*.azure.com``), the client acquires an Entra token via DefaultAzureCredential
and sends it as ``Authorization: Bearer <token>``. Requires you to be signed in
via ``az login`` (or any credential DefaultAzureCredential can resolve).

Usage:
    python clients/test_files_endpoint.py                 # local server on :8088
    python clients/test_files_endpoint.py --url <deployed>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

DEFAULT_URL = "http://localhost:8088"
SAMPLE = Path(__file__).parent / "sample.txt"

# Scope for Foundry / Azure AI cognitive endpoints
FOUNDRY_SCOPE = "https://ai.azure.com/.default"

# Data-plane API version required by Foundry hosted-agent endpoints
DEFAULT_API_VERSION = "v1"


def _needs_auth(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host.endswith(".azure.com") or host.endswith(".azure.net")


def _auth_headers(url: str) -> dict[str, str]:
    if not _needs_auth(url):
        return {}
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError:
        print(
            "!!! azure-identity not installed. Install it or run against localhost.",
            file=sys.stderr,
        )
        raise
    print(f"    (acquiring Entra token for {FOUNDRY_SCOPE})")
    token = DefaultAzureCredential().get_token(FOUNDRY_SCOPE).token
    return {"Authorization": f"Bearer {token}"}


def _with_api_version(url: str, api_version: str | None) -> str:
    if not api_version:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}api-version={api_version}"


def upload(
    client: httpx.Client,
    base_url: str,
    path: Path,
    media_type: str,
    api_version: str | None,
) -> str:
    endpoint = _with_api_version(base_url.rstrip("/") + "/files", api_version)
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
    if r.status_code >= 400:
        print(f"!!! HTTP {r.status_code} from /files")
        print(f"    Response headers: {dict(r.headers)}")
        print(f"    Response body: {r.text}")
        r.raise_for_status()
    body = r.json()
    print(f"<<< Uploaded. Response: {json.dumps(body, indent=2)}")
    return body.get("id") or body.get("file_id") or ""


def send(
    client: httpx.Client,
    base_url: str,
    file_id: str,
    api_version: str | None,
) -> dict:
    endpoint = _with_api_version(base_url.rstrip("/") + "/responses", api_version)
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
    if r.status_code >= 400:
        print(f"!!! HTTP {r.status_code} from /responses")
        print(f"    Response body: {r.text}")
        r.raise_for_status()
    return r.json()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Hosted agent base URL")
    parser.add_argument("--file", default=str(SAMPLE), help="File to upload")
    parser.add_argument("--media-type", default="text/plain", help="MIME type")
    parser.add_argument(
        "--api-version",
        default=None,
        help=(
            f"Foundry data-plane API version. Auto-applied for Azure URLs "
            f"(default: {DEFAULT_API_VERSION}). Not sent for localhost."
        ),
    )
    args = parser.parse_args()

    path = Path(args.file)
    headers = _auth_headers(args.url)
    api_version = args.api_version or (DEFAULT_API_VERSION if _needs_auth(args.url) else None)

    with httpx.Client(timeout=120.0, headers=headers) as client:
        file_id = upload(client, args.url, path, args.media_type, api_version)
        if not file_id:
            print("!!! Upload succeeded but no file id returned - cannot continue.")
            return 1
        body = send(client, args.url, file_id, api_version)

    print("<<< /responses body:")
    print(json.dumps(body, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
