"""Pydantic models for Discord webhook payloads.

FastMCP auto-generates JSON Schema from these so LLMs see the exact
shape of data they need to provide.
"""

from enum import IntFlag
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class EmbedFooter(BaseModel):
    """Footer shown at the bottom of an embed."""

    text: Annotated[str, Field(description="Footer text", max_length=2048)]
    icon_url: Annotated[str | None, Field(description="Footer icon URL")] = None


class EmbedImage(BaseModel):
    """Image displayed in an embed."""

    url: Annotated[
        str,
        Field(description="Source URL (http/https or attachment://filename)"),
    ]


class EmbedAuthor(BaseModel):
    """Author info shown at the top of an embed."""

    name: Annotated[str, Field(description="Author name", max_length=256)]
    url: Annotated[str | None, Field(description="Author link URL")] = None
    icon_url: Annotated[str | None, Field(description="Author icon URL")] = None


class EmbedField(BaseModel):
    """A single field in an embed (key-value pair)."""

    name: Annotated[str, Field(description="Field name", max_length=256)]
    value: Annotated[str, Field(description="Field value", max_length=1024)]
    inline: Annotated[
        bool | None,
        Field(description="Display inline with other fields"),
    ] = None


class Embed(BaseModel):
    """A rich embed object for Discord messages."""

    title: Annotated[str | None, Field(description="Embed title", max_length=256)] = (
        None
    )
    description: Annotated[
        str | None,
        Field(description="Rich text content (max 4096 chars)", max_length=4096),
    ] = None
    url: Annotated[str | None, Field(description="URL the title links to")] = None
    timestamp: Annotated[
        str | None,
        Field(description="ISO8601 timestamp"),
    ] = None
    color: Annotated[
        int | None,
        Field(
            description=(
                "Decimal color for left border. "
                "Common: 3066993 (green), 15158332 (red), "
                "3447003 (blue), 15105570 (orange), 10181046 (purple)"
            ),
        ),
    ] = None
    footer: Annotated[EmbedFooter | None, Field(description="Footer content")] = None
    image: Annotated[EmbedImage | None, Field(description="Large image at bottom")] = (
        None
    )
    thumbnail: Annotated[
        EmbedImage | None, Field(description="Small image at top-right")
    ] = None
    author: Annotated[EmbedAuthor | None, Field(description="Author block at top")] = (
        None
    )
    fields: Annotated[
        list[EmbedField] | None,
        Field(
            description="Field rows (max 25). Use inline=True to group in rows of 3."
        ),
    ] = None


class AllowedMentions(BaseModel):
    """Controls which mentions in the message actually ping users/roles."""

    parse: Annotated[
        list[Literal["roles", "users", "everyone"]] | None,
        Field(
            description=(
                "Mention types to parse. Default: only 'users' pings. "
                "Add 'roles' or 'everyone' to enable those."
            ),
        ),
    ] = None
    roles: Annotated[
        list[str] | None,
        Field(description="Role IDs allowed to mention (max 100)"),
    ] = None
    users: Annotated[
        list[str] | None,
        Field(description="User IDs allowed to mention (max 100)"),
    ] = None


class PollMedia(BaseModel):
    """Text or emoji content for a poll answer."""

    text: Annotated[
        str | None,
        Field(description="Display text (max 300 chars)"),
    ] = None
    emoji_id: Annotated[
        str | None,
        Field(description="Custom emoji ID"),
    ] = None
    emoji_name: Annotated[
        str | None,
        Field(description="Emoji name (e.g. 😀)"),
    ] = None


class PollAnswer(BaseModel):
    """A single answer option in a poll."""

    poll_media: Annotated[
        PollMedia,
        Field(description="Answer content"),
    ]


class Poll(BaseModel):
    """A poll that can be attached to a message."""

    question: Annotated[
        PollMedia,
        Field(description="Poll question content (max 300 chars)"),
    ]
    answers: Annotated[
        list[PollAnswer],
        Field(description="Answer options (2-10 required)"),
    ]
    duration: Annotated[
        int | None,
        Field(
            description="Duration in hours (1-168, default 24)",
            ge=1,
            le=168,
        ),
    ] = None
    allow_multiselect: Annotated[
        bool | None,
        Field(description="Allow multiple selections"),
    ] = None


class MessageFlag(IntFlag):
    """Bitfield flag values for webhook messages."""

    SUPPRESS_EMBEDS = 4
    SUPPRESS_NOTIFICATIONS = 4096


class Button(BaseModel):
    """A link button in a message component row.

    Only link buttons (style 5) work for non-application-owned webhooks.
    Interactive buttons require an application-owned webhook.
    """

    type: int = 2  # Always 2 for button
    style: Literal[5] = 5  # Link button
    label: Annotated[str, Field(description="Button label (max 80 chars)")]
    url: Annotated[
        str,
        Field(description="Button URL (http/https)"),
    ]
    disabled: Annotated[bool, Field(description="Grey out the button")] = False


class ActionRow(BaseModel):
    """A row of up to 5 buttons."""

    type: int = 1  # Always 1 for action row
    components: Annotated[
        list[Button],
        Field(description="Buttons in this row (max 5 per row, max 5 rows)"),
    ]
