"""
Client A - Send a file inline via the OpenAI Responses ``input_file`` content
type.

This is the closest wire-level equivalent of what an Agent Framework client
does when serializing a ``ChatMessage`` that contains a ``DataContent``
alongside a ``TextContent``. It's also the standard OpenAI Responses input
shape for file attachments.

If the server-side ``azure-ai-agentserver-agentframework`` bridge parses
``input_file`` into an Agent Framework ``DataContent``, the agent will describe
the file. If the bridge drops it, the agent will reply
``No attachment received.`` - reproducing the customer's report.

Usage:
    python clients/test_datacontent.py                    # local server on :8088
    python clients/test_datacontent.py --url <deployed>   # deployed hosted agent
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

DEFAULT_URL = "http://localhost:8088"
SAMPLE = Path(__file__).parent / "sample.txt"

FOUNDRY_SCOPE = "https://ai.azure.com/.default"

# Data-plane API version required by Foundry hosted-agent endpoints
DEFAULT_API_VERSION = "v1"


def _needs_auth(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host.endswith(".azure.com") or host.endswith(".azure.net")


def _auth_headers(url: str) -> dict[str, str]:
    if not _needs_auth(url):
        return {}
    from azure.identity import DefaultAzureCredential
    print(f"    (acquiring Entra token for {FOUNDRY_SCOPE})")
    token = DefaultAzureCredential().get_token(FOUNDRY_SCOPE).token
    return {"Authorization": f"Bearer {token}"}


def build_payload(file_bytes: bytes, filename: str, media_type: str) -> dict:
    b64 = base64.b64encode(file_bytes).decode("ascii")
    return {
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Please describe the attached file. Include its media type,"
                            " byte size, and the first 200 characters of the content."
                        ),
                    },
                    {
                        "type": "input_file",
                        "filename": filename,
                        "file_data": f"data:{media_type};base64,{b64}",
                    },
                ],
            }
        ],
        "stream": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Hosted agent base URL")
    parser.add_argument("--file", default=str(SAMPLE), help="File to attach")
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
    data = path.read_bytes()
    payload = build_payload(data, path.name, args.media_type)

    endpoint = args.url.rstrip("/") + "/responses"
    api_version = args.api_version or (DEFAULT_API_VERSION if _needs_auth(args.url) else None)
    if api_version:
        sep = "&" if "?" in endpoint else "?"
        endpoint = f"{endpoint}{sep}api-version={api_version}"
    print(f">>> POST {endpoint}")
    print(f"    Attaching {path.name} ({len(data)} bytes, {args.media_type})")
    print(f"    Content types: {[c['type'] for c in payload['input'][0]['content']]}")
    print()

    headers = _auth_headers(args.url)
    with httpx.Client(timeout=120.0, headers=headers) as client:
        r = client.post(endpoint, json=payload)
        if r.status_code >= 400:
            print(f"!!! HTTP {r.status_code} from /responses")
            print(f"    Response body: {r.text}")
            r.raise_for_status()
        body = r.json()

    print("<<< Response:")
    print(json.dumps(body, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
