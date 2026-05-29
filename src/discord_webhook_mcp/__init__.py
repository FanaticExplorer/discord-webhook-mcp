"""Discord Webhook MCP server.

Set DISCORD_WEBHOOK_URL in your environment, then run:

    python -m discord_webhook_mcp
"""

from fastmcp import FastMCP

from . import server

mcp = FastMCP(
    "Discord Webhook",
    instructions=(
        "Send messages to Discord via webhooks. "
        "Use send_webhook_message for one-off notifications, "
        "and edit/delete with the returned message_id for updates."
    ),
)

server.register(mcp)


def main() -> None:
    """Run the Discord Webhook MCP server."""
    mcp.run()
