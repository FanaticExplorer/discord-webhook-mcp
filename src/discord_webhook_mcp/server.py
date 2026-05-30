"""MCP tool definitions for Discord webhooks.

Thin wrappers — validate inputs, delegate to client.py, return results.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from . import client
from .models import ActionRow, AllowedMentions, Embed, MessageFlag, Poll


def register(mcp: FastMCP) -> None:
    """Register all Discord webhook tools on a FastMCP server instance."""

    @mcp.tool(annotations={"readOnlyHint": False})
    async def send_webhook_message(
        content: Annotated[
            str | None,
            Field(description="Message text (max 2000 chars)"),
        ] = None,
        username: Annotated[
            str | None,
            Field(description="Custom display name"),
        ] = None,
        avatar_url: Annotated[
            str | None,
            Field(description="Custom avatar URL"),
        ] = None,
        tts: Annotated[bool, Field(description="Text-to-speech message")] = False,
        embeds: Annotated[
            list[Embed] | None,
            Field(description="Up to 10 embed objects"),
        ] = None,
        allowed_mentions: Annotated[
            AllowedMentions | None,
            Field(description="Restrict which @mentions ping"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(description="Send to a specific thread"),
        ] = None,
        flags: Annotated[
            list[str] | None,
            Field(
                description="Message flags. Options: 'SUPPRESS_EMBEDS' (hide previews), "
                "'SUPPRESS_NOTIFICATIONS' (silent)"
            ),
        ] = None,
        poll: Annotated[
            Poll | None,
            Field(description="Poll to attach (2-10 answers)"),
        ] = None,
        thread_name: Annotated[
            str | None,
            Field(
                description="Thread name (creates new thread in forum/media channels)"
            ),
        ] = None,
        applied_tags: Annotated[
            list[str] | None,
            Field(description="Tag IDs for new thread (forum/media only)"),
        ] = None,
        components: Annotated[
            list[ActionRow] | None,
            Field(description="Up to 5 action rows with link buttons"),
        ] = None,
        wait: Annotated[
            bool,
            Field(description="Wait for confirmation (returns message ID)"),
        ] = True,
    ) -> dict:
        """Post a message to Discord. Supports text, embeds, polls, link
        buttons, silent flags, and forum thread creation (use thread_name)."""
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

        flag_bits = int(sum(MessageFlag[f] for f in flags)) if flags else None
        return await client.send_message(
            payload,
            wait=wait,
            thread_id=thread_id,
            flags=flag_bits,
            poll=poll,
            thread_name=thread_name,
            applied_tags=applied_tags,
            components=components,
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
        """Fetch a previously-sent message. Useful for reading poll results."""
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
            Field(description="New message text (max 2000 chars)"),
        ] = None,
        embeds: Annotated[
            list[Embed] | None,
            Field(description="Replacement embeds (up to 10)"),
        ] = None,
        allowed_mentions: Annotated[
            AllowedMentions | None,
            Field(description="New allowed mentions config"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(description="Thread ID"),
        ] = None,
        components: Annotated[
            list[ActionRow] | None,
            Field(description="Replacement action rows with link buttons"),
        ] = None,
    ) -> dict:
        """Update content, embeds, or buttons on a message you sent."""
        payload = client.build_message_payload(
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )
        if not payload and not components:
            raise ToolError(
                "At least one of 'content', 'embeds', 'allowed_mentions', "
                "or 'components' must be provided."
            )
        return await client.edit_message(
            message_id, payload, thread_id=thread_id, components=components
        )

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
        """Remove a message."""
        return await client.delete_message(message_id, thread_id=thread_id)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False})
    async def modify_webhook(
        name: Annotated[
            str | None,
            Field(description="Display name (1-80 chars)"),
        ] = None,
        avatar: Annotated[
            str | None,
            Field(description="Base64 image data (data:image/...;base64,...)"),
        ] = None,
    ) -> dict:
        """Rename the webhook and/or change its avatar."""
        return await client.modify_webhook(name=name, avatar=avatar)

    # ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True})
    async def delete_webhook() -> dict:
        """Permanently delete this webhook. Cannot be undone."""
        return await client.delete_webhook()

    # ---

    @mcp.tool(annotations={"readOnlyHint": False})
    async def send_webhook_file(
        file_path: Annotated[
            str,
            Field(description="Local path to the file"),
        ],
        filename: Annotated[
            str | None,
            Field(description="Custom filename shown in Discord"),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="Alt text / description (max 1024 chars)"),
        ] = None,
        content: Annotated[
            str | None,
            Field(description="Optional text caption"),
        ] = None,
        embeds: Annotated[
            list[Embed] | None,
            Field(description="Embeds to include with the file"),
        ] = None,
        username: Annotated[
            str | None,
            Field(description="Custom display name"),
        ] = None,
        avatar_url: Annotated[
            str | None,
            Field(description="Custom avatar URL"),
        ] = None,
        thread_id: Annotated[
            str | None,
            Field(description="Send to a specific thread"),
        ] = None,
        thread_name: Annotated[
            str | None,
            Field(description="Thread name (creates new thread in forum/media)"),
        ] = None,
        applied_tags: Annotated[
            list[str] | None,
            Field(description="Tag IDs for new thread"),
        ] = None,
        components: Annotated[
            list[ActionRow] | None,
            Field(description="Up to 5 action rows with link buttons"),
        ] = None,
        wait: Annotated[
            bool,
            Field(description="Wait for confirmation (returns message ID)"),
        ] = True,
    ) -> dict:
        """Upload a local file to Discord with an optional caption."""
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
            components=components,
        )

    # ---

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_webhook_info() -> dict:
        """Get webhook metadata (name, channel, guild)."""
        return await client.get_info()
