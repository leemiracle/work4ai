# Configure Channels

The gateway is the single entry point for IM platforms, the Web UI, the TUI, and ACP clients. Channels are loaded lazily: a channel and its dependencies are initialized only when its entry exists under `channels` in `config.yaml`.

## Configuration file

Default path: `$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`. When the file is missing, the gateway warns and uses defaults (no IM channel enabled). Changed channel entries are reloaded automatically after the file is saved.

Minimal configuration — explicitly disable all IM channels:

```yaml
channels: {}
```

## Supported channels

| Region | Channel | Config key | Private chat | Group chat |
| --- | --- | --- | --- | --- |
| China | Xiaoyi | `xiaoyi` | Yes | No |
| China | Feishu (Lark) | `feishu` | Yes | Yes (@mention) |
| China | DingTalk | `dingtalk` | Yes | Yes (@mention) |
| China | WeCom | `wecom` | Yes | Yes (@mention) |
| China | Personal WeChat | `wechat` | Yes | No |
| International | Telegram | `telegram` | Yes | Yes (@mention) |
| International | Discord | `discord` | Yes | Yes (@mention) |
| International | Slack | `slack` | Yes | Yes (channel threads) |
| International | WhatsApp | `whatsapp` | Yes | No |

Feishu and WeCom additionally support the group Digital Avatar feature (`group_digital_avatar: true`).

## Common configuration example

Replace the placeholder credentials with real values; other fields can keep their defaults:

```yaml
channels:
  feishu:
    apps:
      - app_id: "cli_xxx"          # Replace with the Feishu app ID
        app_secret: "xxx"          # Replace with the Feishu app secret
        allow_from: []             # Empty means unrestricted; add open_ids to allow-list
        group_digital_avatar: false

  telegram:
    bot_token: "123456:ABC"        # Replace with the token from BotFather
    allow_from: []
    group_chat_mode: mention       # mention / always

  dingtalk:
    client_id: "xxx"               # Replace with the DingTalk client ID
    client_secret: "xxx"           # Replace with the DingTalk client secret
```

## Channel options

| Channel | Main options |
| --- | --- |
| `feishu` | `apps[]`: `app_id`, `app_secret`, `encrypt_key`, `verification_token`, `allow_from`, `enable_streaming`, `group_digital_avatar`, `my_user_id`, `bot_name` |
| `xiaoyi` | `apps[]`: `ak`, `sk`, `agent_id`, `api_id`, `enable_streaming` |
| `dingtalk` | `client_id`, `client_secret`, `allow_from` |
| `telegram` | `bot_token`, `allow_from`, `parse_mode`, `group_chat_mode` |
| `discord` | `bot_token`, `application_id`, `guild_id`, `channel_id`, `allow_from`, `block_dm` |
| `slack` | `bot_token`, `app_token`, `allow_from`, `allowed_channel_ids`, `default_channel_id`, `reply_in_thread` |
| `wecom` | `bot_id`, `secret`, `ws_url`, `allow_from`, `enable_streaming`, `group_digital_avatar` |
| `wechat` | `base_url`, `bot_token`, `ilink_bot_id`, `ilink_user_id`, `allow_from`, `auto_login` |
| `whatsapp` | `bridge_ws_url`, `allow_from`, `default_jid`, `enable_streaming`, `auto_start_bridge` |

## Platform credentials

App creation, permission requests, and credential acquisition differ per platform and are maintained in the external platform documentation:

- China channels: [China Channels](https://gitcode.com/openJiuwen/jiuwenswarm/blob/develop/docs/en/ChinaChannels.md)
- International channels: [International Channels](https://gitcode.com/openJiuwen/jiuwenswarm/blob/develop/docs/en/InternationalChannels.md)

## Verify

1. Start the gateway; the log should contain `[ExtensionManager] 加载 ...` and the registration log for the channel.
2. If the log shows `channels.<name> missing or invalid`, check the config key and required credentials.
3. If a channel does not start, make sure it is not explicitly set to `enabled: false` and that required credentials are non-empty.

---

## Navigation

- [Documentation home](../../README.md)
- [Quick Start](../tutorial/01-quick-start.md)
- [Local validation](local-validation.md)
