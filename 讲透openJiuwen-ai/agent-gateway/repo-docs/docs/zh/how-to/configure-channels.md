# 配置频道

Gateway 是 IM 平台、Web UI、TUI 与 ACP 客户端的统一接入层。频道按需惰性加载：只有 `config.yaml` 的 `channels` 中出现对应条目时，才会初始化该频道及其依赖。

## 配置文件

默认路径：`$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`。文件不存在时 Gateway 告警并使用默认值（不启用任何 IM 频道）。修改保存后，Gateway 会自动重载发生变化的频道配置。

最小配置——显式关闭所有 IM 频道：

```yaml
channels: {}
```

## 支持的频道

| 区域 | 频道 | 配置键 | 私聊 | 群聊 |
| --- | --- | --- | --- | --- |
| 国内 | 小艺 | `xiaoyi` | 支持 | 不支持 |
| 国内 | 飞书 | `feishu` | 支持 | 支持（@机器人） |
| 国内 | 钉钉 | `dingtalk` | 支持 | 支持（@机器人） |
| 国内 | 企业微信 | `wecom` | 支持 | 支持（@机器人） |
| 国内 | 个人微信 | `wechat` | 支持 | 不支持 |
| 海外 | Telegram | `telegram` | 支持 | 支持（@机器人） |
| 海外 | Discord | `discord` | 支持 | 支持（@机器人） |
| 海外 | Slack | `slack` | 支持 | 支持（频道线程） |
| 海外 | WhatsApp | `whatsapp` | 支持 | 不支持 |

飞书与企业微信额外支持群聊数字分身（`group_digital_avatar: true`）。

## 常用配置示例

下面的占位值需要替换为真实凭据，其余字段可保持默认：

```yaml
channels:
  feishu:
    apps:
      - app_id: "cli_xxx"          # 替换为飞书应用 App ID
        app_secret: "xxx"          # 替换为飞书应用 App Secret
        allow_from: []             # 空表示不限制；填写 open_id 可加白名单
        group_digital_avatar: false

  telegram:
    bot_token: "123456:ABC"        # 替换为 BotFather 提供的 token
    allow_from: []
    group_chat_mode: mention       # mention / always

  dingtalk:
    client_id: "xxx"               # 替换为钉钉应用 Client ID
    client_secret: "xxx"           # 替换为钉钉应用 Client Secret
```

## 各频道配置项

| 频道 | 主要配置项 |
| --- | --- |
| `feishu` | `apps[]`：`app_id`、`app_secret`、`encrypt_key`、`verification_token`、`allow_from`、`enable_streaming`、`group_digital_avatar`、`my_user_id`、`bot_name` |
| `xiaoyi` | `apps[]`：`ak`、`sk`、`agent_id`、`api_id`、`enable_streaming` |
| `dingtalk` | `client_id`、`client_secret`、`allow_from` |
| `telegram` | `bot_token`、`allow_from`、`parse_mode`、`group_chat_mode` |
| `discord` | `bot_token`、`application_id`、`guild_id`、`channel_id`、`allow_from`、`block_dm` |
| `slack` | `bot_token`、`app_token`、`allow_from`、`allowed_channel_ids`、`default_channel_id`、`reply_in_thread` |
| `wecom` | `bot_id`、`secret`、`ws_url`、`allow_from`、`enable_streaming`、`group_digital_avatar` |
| `wechat` | `base_url`、`bot_token`、`ilink_bot_id`、`ilink_user_id`、`allow_from`、`auto_login` |
| `whatsapp` | `bridge_ws_url`、`allow_from`、`default_jid`、`enable_streaming`、`auto_start_bridge` |

## 平台凭据获取

各平台的应用创建、权限申请与凭据获取步骤较长，统一维护在外部平台接入文档中：

- [国内频道](https://gitcode.com/openJiuwen/jiuwenswarm/blob/develop/docs/zh/国内频道.md)
- [海外频道](https://gitcode.com/openJiuwen/jiuwenswarm/blob/develop/docs/zh/海外频道.md)

## 验证

1. 启动 Gateway，日志中应出现 `[ExtensionManager] 加载 ...` 以及对应频道的注册日志。
2. 若日志显示 `channels.<name> missing or invalid`，检查配置键名与必填凭据。
3. 若频道未启动，确认该条目没有显式设置 `enabled: false`，且必填凭据非空。

---

## 返回导航

- [返回文档首页](../../README.md)
- [快速开始](../tutorial/01-quick-start.md)
- [本地功能验证](local-validation.md)
