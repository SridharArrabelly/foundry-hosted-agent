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

import httpx

DEFAULT_URL = "http://localhost:8088"
SAMPLE = Path(__file__).parent / "sample.txt"


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
    args = parser.parse_args()

    path = Path(args.file)
    data = path.read_bytes()
    payload = build_payload(data, path.name, args.media_type)

    endpoint = args.url.rstrip("/") + "/responses"
    print(f">>> POST {endpoint}")
    print(f"    Attaching {path.name} ({len(data)} bytes, {args.media_type})")
    print(f"    Content types: {[c['type'] for c in payload['input'][0]['content']]}")
    print()

    with httpx.Client(timeout=120.0) as client:
        r = client.post(endpoint, json=payload)
        r.raise_for_status()
        body = r.json()

    print("<<< Response:")
    print(json.dumps(body, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
