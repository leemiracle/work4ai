> 来源: [https://deepwiki.com/Tencent/WeKnora/13-instant-messaging-integrations](https://deepwiki.com/Tencent/WeKnora/13-instant-messaging-integrations)
> DeepWiki Tencent/WeKnora

# Instant Messaging Integrations

  Relevant source files 
 - [frontend/src/api/agent/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/agent/index.ts)
 - [frontend/src/components/IMChannelPanel.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/IMChannelPanel.vue)
 - [internal/handler/im.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/im.go)
 - [internal/im/adapter.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go)
 - [internal/im/feishu/adapter.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/adapter.go)
 - [internal/im/feishu/adapter_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/adapter_test.go)
 - [internal/im/feishu/factory.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/factory.go)
 - [internal/im/feishu/longconn.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/longconn.go)
 - [internal/im/feishu/longconn_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/longconn_test.go)
 - [internal/im/feishu/region_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/region_test.go)
 - [internal/im/feishu/send_e2e_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/send_e2e_test.go)
 - [internal/im/feishu/stream_reaper_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/stream_reaper_test.go)
 - [internal/im/full_output_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/full_output_test.go)
 - [internal/im/service.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go)
 - [internal/im/stream_delivery_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/stream_delivery_test.go)
 - [internal/im/types.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go)
 
  This page provides a high-level overview of WeKnora's Instant Messaging (IM) integration layer, which connects LLM-powered agents and knowledge bases to various messaging platforms. For detailed architecture, adapter mechanics, and configuration instructions, refer to the child pages: [IM Integration Architecture](https://deepwiki.com/Tencent/WeKnora/13.1-im-integration-architecture) and [Platform-Specific Adapters](https://deepwiki.com/Tencent/WeKnora/13.2-platform-specific-adapters).

 Sources: [internal/im/service.go1-50](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L1-L50) [internal/im/adapter.go1-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L1-L30)

 
## System Overview

 WeKnora enables users to interact with agents directly within external workflows on platforms like Feishu, WeCom, DingTalk, Slack, Telegram, and others. The integration is coordinated through a unified `im.Service` [internal/im/service.go1-38](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L1-L38) that interfaces with platform adapters [internal/im/adapter.go125-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L125-L144) and persists channels using the `IMChannel` GORM model [internal/im/types.go16-34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L16-L34)

 
### Code-to-System Mapping

 The following diagram illustrates how user-facing IM requests map to backend code entities.

 **IM Integration Component Mapping**

 
```

```

 Sources: [internal/handler/im.go35-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/im.go#L35-L45) [internal/im/service.go36-38](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L36-L38) [internal/im/adapter.go48-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L48-L144) [internal/im/types.go16-34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L16-L34)

 
## IM Integration Architecture

 The IM subsystem employs an adapter pattern to handle diverse platform protocols while maintaining unified session routing, deduplication, and streaming management [internal/im/service.go40-70](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L40-L70) Channels link a platform identity to an `Agent` [internal/im/types.go18-21](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L18-L21) supporting both `user` and `thread` session scoping [internal/im/adapter.go28-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L28-L36) Outbound content is cleaned to strip frontend-specific citation tags (`<kb .../>`, `<web .../>`) [internal/im/service.go71-79](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L71-L79) and internal storage URLs are rewritten to HTTP URLs [internal/im/service.go101-110](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L101-L110) for correct rendering in chat clients.

 For detailed architecture, stream buffering, incomplete XML tag handling, and the unified service layer, see [IM Integration Architecture](https://deepwiki.com/Tencent/WeKnora/13.1-im-integration-architecture).

 Sources: [internal/im/service.go40-110](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L40-L110) [internal/im/adapter.go28-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L28-L36) [internal/im/types.go16-34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L16-L34)

 
## Supported Platforms and Adapters

 WeKnora supports a comprehensive set of IM platforms via specialized adapters that conform to the `im.Adapter` interface [internal/im/adapter.go125-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L125-L144) Optional interfaces such as `StreamSender` and `FileDownloader` enable real-time streaming and file attachment handling [internal/im/adapter.go146-174](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L146-L174)

 
| Platform | Supported Modes | Key Features & Notes |
|---|---|---|
| Feishu / Lark | Webhook, WebSocket | Uses CardKit streaming update API; supports multi-cloud region selection internal/im/feishu/adapter.go53-89 |
| WeCom (企业微信) | Webhook, WebSocket (longconn) | Supports long connection via WebSocket; parses quote-reply messages internal/im/wecom/longconn.go1-60 |
| DingTalk (钉钉) | Webhook, Stream | Uses client ID credentials for identity, supports streaming output internal/im/types.go189-192 |
| Slack | Webhook, Socket Mode | Supports thread conversations with thread_ts internal/im/adapter.go70-79 |
| Telegram | Webhook | Supports forum topics thread via message_thread_id internal/im/adapter.go70-79 |
| Others | Various | Mattermost, QQBot, Yunzhijia, WeChat long-polling mode internal/handler/im.go18-21 |

 
### Unified Message Pipeline Flow

 
```

```

 Sources: [internal/handler/im.go35-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/im.go#L35-L45) [internal/im/service.go36-38](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/service.go#L36-L38) [internal/im/adapter.go125-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L125-L144) [internal/im/feishu/adapter.go195-211](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/feishu/adapter.go#L195-L211)

 For full configuration, webhook setup, and platform-specific behavior, see [Platform-Specific Adapters](https://deepwiki.com/Tencent/WeKnora/13.2-platform-specific-adapters).

 Sources: [internal/handler/im.go18-21](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/im.go#L18-L21) [internal/im/adapter.go70-144](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/adapter.go#L70-L144) [internal/im/types.go189-192](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L189-L192)

 
## Management Interface

 Administrators configure and manage IM channels through the **IM Channel Panel** in the frontend, which interacts with the channel CRUD endpoints handled by `IMHandler` [internal/handler/im.go35-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/im.go#L35-L45) Channels are validated and uniquely identified by computing a `bot_identity` string from their credentials, preventing duplicate bot registrations [internal/im/types.go28-30](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L28-L30) [internal/im/types.go143-158](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L143-L158)

 
### Bot Identity Computation Diagram

 
```

```

 Sources: [internal/im/types.go16-34](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L16-L34) [internal/im/types.go143-190](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/im/types.go#L143-L190) [frontend/src/components/IMChannelPanel.vue1-135](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/IMChannelPanel.vue#L1-L135)

 For platform-specific setup instructions and parameter references, see [Platform-Specific Adapters](https://deepwiki.com/Tencent/WeKnora/13.2-platform-specific-adapters).
