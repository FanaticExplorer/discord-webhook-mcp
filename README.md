# Discord Webhook MCP Server

MCP server that lets coding agents send messages to Discord via webhooks.

## Setup

Set the `DISCORD_WEBHOOK_URL` environment variable to your webhook URL:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1234567890/abc123xyz"
```

## Tools

| Tool | Description |
|---|---|
| `send_webhook_message` | Send a message with content, embeds, custom username/avatar |
| `get_webhook_message` | Retrieve a previously-sent message by ID |
| `edit_webhook_message` | Edit an existing webhook message |
| `delete_webhook_message` | Delete a webhook message (cannot be undone) |
| `get_webhook_info` | Get webhook metadata (name, channel, guild) |

## Example Usage

```
send_webhook_message(content="Build succeeded! :rocket:")

send_webhook_message(embeds=[{
    "title": "CI Pipeline",
    "description": "All checks passed",
    "color": 3066993,
    "fields": [
        {"name": "Branch", "value": "main", "inline": true},
        {"name": "Commit", "value": "abc1234", "inline": true}
    ]
}])
```
