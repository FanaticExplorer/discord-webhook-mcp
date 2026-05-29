"""HTTP client for Discord webhook API.

Pure HTTP layer — no FastMCP dependency.  Takes a webhook URL, makes
requests, and returns parsed responses or raises ToolError.
"""

from __future__ import annotations

import json
import mimetypes
import os
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

import httpx
from fastmcp.exceptions import ToolError

from .models import AllowedMentions, Embed

# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------


def get_webhook_url() -> str:
    """Return the webhook URL from DISCORD_WEBHOOK_URL env var."""
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        raise ToolError(
            "DISCORD_WEBHOOK_URL environment variable is not set. "
            "Set DISCORD_WEBHOOK_URL to your webhook URL."
        )
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# Payload builder (shared by send & edit)
# ---------------------------------------------------------------------------


def _serialize_embeds(embeds: Sequence[Embed | dict]) -> list[dict]:
    """Accept Embed models or raw dicts, return API-ready dicts."""
    out: list[dict] = []
    for e in embeds:
        if isinstance(e, dict):
            out.append(Embed(**e).model_dump(exclude_none=True))
        else:
            out.append(e.model_dump(exclude_none=True))
    return out


def build_message_payload(
    *,
    content: str | None = None,
    username: str | None = None,
    avatar_url: str | None = None,
    tts: bool = False,
    embeds: Sequence[Embed | dict] | None = None,
    allowed_mentions: AllowedMentions | None = None,
) -> dict:
    """Build the JSON payload for a webhook message (send or edit)."""
    payload: dict = {}
    if content is not None:
        payload["content"] = str(content)
    if username is not None:
        payload["username"] = username
    if avatar_url is not None:
        payload["avatar_url"] = avatar_url
    if tts:
        payload["tts"] = True
    if embeds:
        payload["embeds"] = _serialize_embeds(embeds)
    if allowed_mentions is not None:
        payload["allowed_mentions"] = allowed_mentions.model_dump(exclude_none=True)
    return payload


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def _raise_api_error(response: httpx.Response) -> NoReturn:
    """Parse a Discord error response and raise ToolError."""
    try:
        body = response.json()
        msg = body.get("message", response.text)
        code = body.get("code", "unknown")
        raise ToolError(f"Discord API error {response.status_code} [{code}]: {msg}")
    except ToolError:
        raise
    except Exception:
        raise ToolError(f"Discord API returned {response.status_code}: {response.text}")


# ---------------------------------------------------------------------------
# API methods
# ---------------------------------------------------------------------------


async def send_message(
    payload: dict,
    *,
    wait: bool = True,
    thread_id: str | None = None,
) -> dict:
    """POST a message to the webhook URL. Returns the message object or status."""
    params: dict[str, str] = {}
    if wait:
        params["wait"] = "true"
    if thread_id:
        params["thread_id"] = thread_id

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(get_webhook_url(), json=payload, params=params)

    if response.status_code == 204:
        return {"status": "sent"}
    if response.status_code in (200, 201):
        return response.json()
    _raise_api_error(response)


async def get_message(
    message_id: str,
    *,
    thread_id: str | None = None,
) -> dict:
    """GET a previously-sent webhook message."""
    params = {"thread_id": thread_id} if thread_id else None
    url = f"{get_webhook_url()}/messages/{message_id}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    _raise_api_error(response)


async def edit_message(
    message_id: str,
    payload: dict,
    *,
    thread_id: str | None = None,
) -> dict:
    """PATCH an existing webhook message."""
    params = {"thread_id": thread_id} if thread_id else None
    url = f"{get_webhook_url()}/messages/{message_id}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.patch(url, json=payload, params=params)

    if response.status_code == 200:
        return response.json()
    _raise_api_error(response)


async def delete_message(
    message_id: str,
    *,
    thread_id: str | None = None,
) -> dict:
    """DELETE a webhook message."""
    params = {"thread_id": thread_id} if thread_id else None
    url = f"{get_webhook_url()}/messages/{message_id}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.delete(url, params=params)

    if response.status_code == 204:
        return {"status": "deleted", "message_id": message_id}
    _raise_api_error(response)


async def modify_webhook(
    *,
    name: str | None = None,
    avatar: str | None = None,
) -> dict:
    """PATCH the webhook itself — change name and/or avatar."""
    payload: dict = {}
    if name is not None:
        payload["name"] = name
    if avatar is not None:
        payload["avatar"] = avatar

    if not payload:
        raise ToolError("At least one of 'name' or 'avatar' must be provided.")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.patch(get_webhook_url(), json=payload)

    if response.status_code == 200:
        return response.json()
    _raise_api_error(response)


async def send_file(
    file_path: str,
    *,
    filename: str | None = None,
    description: str | None = None,
    content: str | None = None,
    embeds: Sequence[Embed | dict] | None = None,
    username: str | None = None,
    avatar_url: str | None = None,
    wait: bool = True,
    thread_id: str | None = None,
) -> dict:
    """POST a message with a file attachment via multipart/form-data."""
    path = Path(file_path)
    if not path.is_file():
        raise ToolError(f"File not found: {file_path}")

    name = filename or path.name
    mime_type, _ = mimetypes.guess_type(str(path))
    file_bytes = path.read_bytes()

    json_body: dict = {
        "attachments": [{"id": 0, "filename": name}],
    }
    if description:
        json_body["attachments"][0]["description"] = description
    if content is not None:
        json_body["content"] = content
    if embeds:
        json_body["embeds"] = _serialize_embeds(embeds)
    if username is not None:
        json_body["username"] = username
    if avatar_url is not None:
        json_body["avatar_url"] = avatar_url

    params: dict[str, str] = {}
    if wait:
        params["wait"] = "true"
    if thread_id:
        params["thread_id"] = thread_id

    form_data = {
        "payload_json": (None, json.dumps(json_body), "application/json"),
        "files[0]": (name, file_bytes, mime_type or "application/octet-stream"),
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            get_webhook_url(),
            files=form_data,
            params=params,
        )

    if response.status_code == 204:
        return {"status": "sent"}
    if response.status_code in (200, 201):
        return response.json()
    _raise_api_error(response)


async def get_info() -> dict:
    """GET webhook metadata (name, channel, guild)."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(get_webhook_url())

    if response.status_code == 200:
        return response.json()
    _raise_api_error(response)
