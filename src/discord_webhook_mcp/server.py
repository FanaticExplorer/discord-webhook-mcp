"""MCP tool definitions for Discord webhooks.

Thin wrappers — validate inputs, delegate to client.py, return results.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from . import client
from .models import AllowedMentions, Embed, MessageFlag, Poll


def register(mcp: FastMCP) -> None:
    """Register all Discord webhook tools on a FastMCP server instance."""

    @mcp.tool(annotations={"readOnlyHint": False})
    async def send_webhook_message(
        content: Annotated[
            str | None,
            Field(description="Plain text message content (up to 2000 characters)"),
        ] = None,
        username: Annotated[
            str | None,
            Field(description="Override the default webhook display name"),
        ] = None,
        avatar_url: Annotated[
            str | None,
            Field(description="Override the default webhook avatar image URL"),
        ] = None,
        tts: Annotated[
            bool, Field(description="Send as a text-to-speech message")
        ] = False,
        embeds: Annotated[
            list[Embed] | None,
            Field(description="Up to 10 rich embed objects for formatted content"),
        ] = None,
        allowed_mentions: Annotated[
            AllowedMentions | None,
            Field(description="Restrict which @mentions actually trigger pings"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(
                description="Send message to a specific thread instead of the main channel"
            ),
        ] = None,
        flags: Annotated[
            list[str] | None,
            Field(
                description="Message flags to set. Values: 'SUPPRESS_EMBEDS' (hides link previews), "
                "'SUPPRESS_NOTIFICATIONS' (silent message, no push/ping)"
            ),
        ] = None,
        poll: Annotated[
            Poll | None,
            Field(description="A poll to attach to the message (2-10 answers)"),
        ] = None,
        thread_name: Annotated[
            str | None,
            Field(
                description="Name for a new thread in a forum/media channel. "
                "Creates a properly-titled thread instead of dumping into the feed."
            ),
        ] = None,
        applied_tags: Annotated[
            list[str] | None,
            Field(
                description="Tag IDs to apply to the new thread (forum/media channels only)"
            ),
        ] = None,
        wait: Annotated[
            bool,
            Field(
                description="Wait for Discord to confirm and return the created message "
                "(includes the message id for later editing/deleting)"
            ),
        ] = True,
    ) -> dict:
        """Send a message to a Discord channel via webhook.

        At least one of 'content' or 'embeds' must be provided.  The returned
        message object includes an 'id' field that can be used with
        get_webhook_message / edit_webhook_message / delete_webhook_message.

        Simple text example:
            content="Build #42 succeeded! :rocket:"

        Embed example:
            embeds=[{
                "title": "Build #42",
                "description": "All 156 tests passed",
                "color": 3066993,
                "fields": [{"name": "Branch", "value": "main", "inline": True}]
            }]

        Poll example:
            poll={
                "question": {"text": "Deploy to production?"},
                "answers": [
                    {"poll_media": {"text": "Yes"}},
                    {"poll_media": {"text": "No"}}
                ]
            }

        Silent message (no notification):
            flags=["SUPPRESS_NOTIFICATIONS"]
        """
        if not content and not embeds and not poll:
            raise ToolError(
                "At least one of 'content', 'embeds', or 'poll' must be provided."
            )

        payload = client.build_message_payload(
            content=content,
            username=username,
            avatar_url=avatar_url,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )

        flag_bits = MessageFlag.from_names(flags) if flags else None
        return await client.send_message(
            payload,
            wait=wait,
            thread_id=thread_id,
            flags=flag_bits,
            poll=poll,
            thread_name=thread_name,
            applied_tags=applied_tags,
        )

    # ---

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_webhook_message(
        message_id: Annotated[
            str,
            Field(description="The ID of a message previously sent by this webhook"),
        ],
        thread_id: Annotated[
            str | None,
            Field(description="Thread ID if the message is in a thread"),
        ] = None,
    ) -> dict:
        """Retrieve a previously-sent webhook message by its ID.

        Returns the full message object including content, embeds, author, and
        timestamp.
        """
        return await client.get_message(message_id, thread_id=thread_id)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False})
    async def edit_webhook_message(
        message_id: Annotated[
            str,
            Field(description="The ID of the message to edit"),
        ],
        content: Annotated[
            str | None,
            Field(description="New plain text content (up to 2000 characters)"),
        ] = None,
        embeds: Annotated[
            list[Embed] | None,
            Field(
                description="New array of up to 10 embed objects (replaces existing)"
            ),
        ] = None,
        allowed_mentions: Annotated[
            AllowedMentions | None,
            Field(description="New allowed mentions configuration"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(description="Thread ID if the message is in a thread"),
        ] = None,
    ) -> dict:
        """Edit a previously-sent webhook message.

        Only provide the fields you want to change — all parameters are optional.
        Returns the updated message object.
        """
        payload = client.build_message_payload(
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )
        if not payload:
            raise ToolError(
                "At least one of 'content', 'embeds', or 'allowed_mentions' "
                "must be provided."
            )
        return await client.edit_message(message_id, payload, thread_id=thread_id)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True})
    async def delete_webhook_message(
        message_id: Annotated[
            str,
            Field(description="The ID of the message to delete"),
        ],
        thread_id: Annotated[
            str | None,
            Field(description="Thread ID if the message is in a thread"),
        ] = None,
    ) -> dict:
        """Delete a message previously sent by this webhook.

        This cannot be undone. Returns confirmation on success.
        """
        return await client.delete_message(message_id, thread_id=thread_id)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False})
    async def modify_webhook(
        name: Annotated[
            str | None,
            Field(description="New display name for the webhook (1-80 characters)"),
        ] = None,
        avatar: Annotated[
            str | None,
            Field(
                description="New avatar for the webhook — base64 image data "
                "(data:image/...;base64,...) or a URL"
            ),
        ] = None,
    ) -> dict:
        """Change the webhook's display name and/or avatar.

        All parameters are optional — only provide what you want to change.
        Returns the updated webhook object.
        """
        return await client.modify_webhook(name=name, avatar=avatar)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True})
    async def delete_webhook() -> dict:
        """Permanently delete this webhook.

        THIS CANNOT BE UNDONE. The webhook URL will stop working immediately.
        """
        return await client.delete_webhook()

    # ---

    @mcp.tool(annotations={"readOnlyHint": False})
    async def send_webhook_file(
        file_path: Annotated[
            str,
            Field(description="Local path to the file to upload"),
        ],
        filename: Annotated[
            str | None,
            Field(description="Override the filename shown in Discord"),
        ] = None,
        description: Annotated[
            str | None,
            Field(
                description="Alt text / description for the file (max 1024 characters)"
            ),
        ] = None,
        content: Annotated[
            str | None,
            Field(description="Optional text message to send alongside the file"),
        ] = None,
        embeds: Annotated[
            list[Embed] | None,
            Field(description="Optional embeds to include alongside the file"),
        ] = None,
        username: Annotated[
            str | None,
            Field(description="Override the default webhook display name"),
        ] = None,
        avatar_url: Annotated[
            str | None,
            Field(description="Override the default webhook avatar image URL"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(description="Send to a specific thread instead of the main channel"),
        ] = None,
        thread_name: Annotated[
            str | None,
            Field(description="Name for a new thread in a forum/media channel"),
        ] = None,
        applied_tags: Annotated[
            list[str] | None,
            Field(description="Tag IDs to apply to the new thread"),
        ] = None,
        wait: Annotated[
            bool,
            Field(
                description="Wait for Discord to confirm and return the created message "
                "(includes the message id for later editing/deleting)"
            ),
        ] = True,
    ) -> dict:
        """Upload a file to a Discord channel via webhook.

        The file at 'file_path' is read from the local filesystem and uploaded
        as a message attachment.  You can optionally include a text message
        and/or embeds alongside the file.

        Supported file types include images, text files, PDFs, and more
        (Discord's 25 MiB limit applies).
        """
        return await client.send_file(
            file_path=file_path,
            filename=filename,
            description=description,
            content=content,
            embeds=embeds,
            username=username,
            avatar_url=avatar_url,
            wait=wait,
            thread_id=thread_id,
            thread_name=thread_name,
            applied_tags=applied_tags,
        )

    # ---

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_webhook_info() -> dict:
        """Get information about this webhook (name, avatar, channel, guild).

        Useful for verifying the webhook URL is valid and checking which
        channel it posts to.
        """
        return await client.get_info()
