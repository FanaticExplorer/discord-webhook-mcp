"""Pydantic models for Discord webhook payloads.

FastMCP auto-generates JSON Schema from these so LLMs see the exact
shape of data they need to provide.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class EmbedFooter(BaseModel):
    """Footer shown at the bottom of an embed."""

    text: Annotated[str, Field(description="Footer text", max_length=2048)]
    icon_url: Annotated[str | None, Field(description="URL of footer icon")] = None


class EmbedImage(BaseModel):
    """Image displayed in an embed."""

    url: Annotated[
        str,
        Field(
            description="Source URL of the image (http/https or attachment://filename)",
        ),
    ]


class EmbedAuthor(BaseModel):
    """Author info shown at the top of an embed."""

    name: Annotated[str, Field(description="Name of author", max_length=256)]
    url: Annotated[str | None, Field(description="URL of author")] = None
    icon_url: Annotated[str | None, Field(description="URL of author icon")] = None


class EmbedField(BaseModel):
    """A single field in an embed (key-value pair)."""

    name: Annotated[str, Field(description="Name of the field", max_length=256)]
    value: Annotated[str, Field(description="Value of the field", max_length=1024)]
    inline: Annotated[
        bool | None,
        Field(description="Whether this field should display inline with others"),
    ] = None


class Embed(BaseModel):
    """A rich embed object for Discord messages."""

    title: Annotated[
        str | None, Field(description="Title of embed", max_length=256)
    ] = None
    description: Annotated[
        str | None, Field(description="Description text", max_length=4096)
    ] = None
    url: Annotated[str | None, Field(description="URL the title links to")] = None
    timestamp: Annotated[
        str | None,
        Field(description="ISO8601 timestamp shown at the bottom of the embed"),
    ] = None
    color: Annotated[
        int | None,
        Field(
            description=(
                "Decimal color code for the embed's left border. "
                "Common values: 3066993 (green), 15158332 (red), "
                "3447003 (blue), 15105570 (orange), 10181046 (purple)"
            ),
        ),
    ] = None
    footer: Annotated[
        EmbedFooter | None, Field(description="Footer shown at bottom")
    ] = None
    image: Annotated[
        EmbedImage | None, Field(description="Large image at bottom of embed")
    ] = None
    thumbnail: Annotated[
        EmbedImage | None, Field(description="Small image at top-right of embed")
    ] = None
    author: Annotated[
        EmbedAuthor | None, Field(description="Author block shown at the top")
    ] = None
    fields: Annotated[
        list[EmbedField] | None,
        Field(
            description="Array of field objects (name/value pairs), max 25. "
            "Use inline=True to put fields side-by-side in rows of up to 3."
        ),
    ] = None


class AllowedMentions(BaseModel):
    """Controls which mentions in the message actually ping users/roles."""

    parse: Annotated[
        list[Literal["roles", "users", "everyone"]] | None,
        Field(
            description=(
                "Types of mentions to parse from the content. "
                "For webhooks, only 'users' is parsed by default. "
                "Include 'roles' to ping roles, 'everyone' for @everyone/@here."
            ),
        ),
    ] = None
    roles: Annotated[
        list[str] | None,
        Field(description="Specific role IDs allowed to mention, max 100"),
    ] = None
    users: Annotated[
        list[str] | None,
        Field(description="Specific user IDs allowed to mention, max 100"),
    ] = None
