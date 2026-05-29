# discord-webhook-mcp

Send Discord messages from any coding agent. Text, embeds, polls, files, link buttons, forum threads — all through a webhook, no bot token needed.

## Tools

| Tool | What it does |
|---|---|
| `send_webhook_message` | Post a message — plain text, embeds, polls, link buttons, or create a forum thread |
| `send_webhook_file` | Upload a local file (image, log, chart, PDF) with an optional caption |
| `get_webhook_message` | Fetch a previously sent message; also how you read live poll results |
| `edit_webhook_message` | Update the content, embeds, or buttons on a message you already sent |
| `delete_webhook_message` | Delete a message |
| `modify_webhook` | Rename the webhook or swap its avatar |
| `delete_webhook` | Permanently delete the webhook |
| `get_webhook_info` | Check the connection and see which channel/guild it posts to |

## Installation

**Prerequisite:** [uv](https://docs.astral.sh/uv/) must be installed.

```bash
uv tool install git+https://github.com/FanaticExplorer/discord-webhook-mcp
```

> Not on PyPI yet. If that's blocking you, open an issue.

## Setup

**1. Create a webhook in Discord**

Go to the channel you want to post in → **Edit Channel → Integrations → Webhooks → New Webhook** → copy the URL.

**2. Add the MCP server to your agent config**

```json
{
  "mcpServers": {
    "discord-webhook": {
      "command": "uvx",
      "args": ["discord-webhook-mcp"],
      "env": {
        "DISCORD_WEBHOOK_URL": "your-webhook-url-here"
      }
    }
  }
}
```

This is the generic config. If you want to contribute to adapt it for your agent, PRs are open.

## Usage examples

**Post a plain message**
```
send_webhook_message(content="Build finished ✅")
```

**Post an embed**
```
send_webhook_message(embeds=[{
  "title": "Test results",
  "description": "47 passed, 0 failed",
  "color": 5763719
}])
```

**Silent message (no push notification)**
```
send_webhook_message(
  content="Deployment started",
  flags=["SUPPRESS_NOTIFICATIONS"]
)
```

**Upload a file**
```
send_webhook_file(
  file_path="/tmp/report.pdf",
  content="Here's the latest report"
)
```

**Create a poll**
```
send_webhook_message(poll={
  "question": {"text": "Which API version should we ship first?"},
  "answers": [
    {"poll_media": {"text": "v2 (stable)"}},
    {"poll_media": {"text": "v3 (beta)"}}
  ],
  "duration": 24
})
```

**Edit a message later**
```
# Save the id returned by send_webhook_message, then:
edit_webhook_message(message_id="...", content="Build finished ✅ (2 warnings)")
```

## Contributing

If you use a coding agent and want to contribute a setup guide for it, PRs are welcome. Same goes for usage examples, bug fixes, or anything else.

## License

[MIT](LICENSE)
