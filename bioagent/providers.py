"""Optional network model adapter. No API call is made by importing this module."""
from __future__ import annotations
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class ModelServiceError(RuntimeError):
    pass


def response_text(payload: dict) -> str:
    if not isinstance(payload, dict) or payload.get("status") != "completed":
        raise ModelServiceError("Model response is not completed")
    pieces = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for block in item.get("content", []):
            if block.get("type") == "output_text" and isinstance(block.get("text"), str):
                pieces.append(block["text"])
    text = "\n".join(pieces).strip()
    if not text:
        raise ModelServiceError("Response has no text output")
    return text


class OpenAITextClient:
    """Explicit text-only Responses API adapter; no automatic tool execution.

    The caller must approve transmission of the prompt to the service. Model IDs
    are supplied by the caller, not hard-coded. Network operation is not covered
    by the offline test suite. See official API documentation before deployment.
    """
    def __init__(self, model: str, api_key: str | None = None, timeout: float = 30):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Explicit model ID required")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required")
        if not 0 < timeout <= 300:
            raise ValueError("Invalid timeout")
        self.timeout = timeout
        self.last_usage = {}

    def complete(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Empty prompt")
        body = json.dumps({"model": self.model, "input": prompt,
                           "max_output_tokens": 2048, "store": False}).encode()
        request = Request("https://api.openai.com/v1/responses", data=body,
                          headers={"Content-Type": "application/json",
                                   "Authorization": "Bearer " + self.api_key}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ModelServiceError("Response exceeds size limit")
            payload = json.loads(raw)
        except HTTPError as exc:
            raise ModelServiceError(f"Model HTTP error {exc.code}; request not retried") from None
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ModelServiceError("Model transport or response error") from None
        self.last_usage = payload.get("usage", {})
        return response_text(payload)
