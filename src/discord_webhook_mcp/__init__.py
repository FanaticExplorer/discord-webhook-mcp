"""Discord Webhook MCP server.

Set DISCORD_WEBHOOK_URL in your environment, then run:

    python -m discord_webhook_mcp
"""

from fastmcp import FastMCP

from . import server

mcp = FastMCP(
    "Discord Webhook",
    instructions=(
        "Post messages, embeds, files, polls, and link buttons to Discord via webhook. "
        "Works in regular channels, threads, and forum channels (with thread creation). "
        "Messages return an id for later editing, deleting, or poll-result checking."
    ),
    dereference_schemas=False,
)

server.register(mcp)


def main() -> None:
    """Run the Discord Webhook MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
