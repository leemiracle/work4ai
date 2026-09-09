> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/6-proxy-and-protocol-bridge-tools](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/6-proxy-and-protocol-bridge-tools)
> DeepWiki deepseek-ai/awesome-deepseek-agent

# Proxy and Protocol Bridge Tools

  Relevant source files 
 - [docs/codex.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1)
 - [docs/codex.zh-CN.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.zh-CN.md?plain=1)
 - [docs/deepseek-droid-guide.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1)
 
  Proxy and protocol bridge tools act as translation layers between agent frameworks and the DeepSeek API. These tools are essential when an agent (such as OpenAI Codex) uses a specific protocol (like the OpenAI Responses API) that differs from DeepSeek's native endpoints. By transforming requests and managing model metadata, these bridges allow users to leverage DeepSeek V4 Pro and Flash models within ecosystems that do not natively support them.

 
### Protocol Translation Architecture

 The following diagram illustrates how a proxy like `moon-bridge` translates specific agent protocols into DeepSeek-compatible requests.

 **Agent-to-DeepSeek Protocol Mapping**

 
```

```

 **Sources:** [docs/codex.md5](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L5-L5) [docs/codex.md39-91](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L39-L91) [docs/codex.md101-105](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L101-L105)

 
---

 
## OpenAI Codex via Moon Bridge

 [OpenAI Codex](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/OpenAI Codex) is a coding agent that communicates exclusively through the OpenAI Responses API [docs/codex.md5](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L5-L5) Because DeepSeek's native reasoning features require specific handling, **Moon Bridge** is used as a forwarding layer [docs/codex.md5](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L5-L5)

 Moon Bridge is configured via a `config.yml` file that defines models, providers, and routes [docs/codex.md39-91](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L39-L91) It specifically supports a `deepseek_v4` extension to ensure compatibility [docs/codex.md58-59](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L58-L59) To integrate with Codex, Moon Bridge provides a utility to generate the necessary `models_catalog.json` and `config.toml` files required by the Codex environment [docs/codex.md107-156](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L107-L156)

 Key configuration components include:

 
 - **Model Identifiers:** `deepseek-v4-pro` and `deepseek-v4-flash` [docs/codex.md46-60](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L46-L60)
 - **Context Window:** Set to `1000000` tokens [docs/codex.md47-61](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L47-L61)
 - **Reasoning Levels:** Support for `high` and `xhigh` effort [docs/codex.md49-68](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L49-L68)
 
 For details on installation, configuration, and the one-command launcher, see [OpenAI Codex via Moon Bridge](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/6.1-openai-codex-via-moon-bridge).

 **Sources:** [docs/codex.md5-105](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L5-L105) [docs/codex.md123-130](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L123-L130) [docs/codex.md180-184](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/codex.md?plain=1#L180-L184)

 
---

 
## Factory AI Droid

 Factory AI Droid is a platform that allows for highly customizable agent configurations through a `settings.json` file located in `~/.factory/` [docs/deepseek-droid-guide.md18](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L18-L18) It supports multiple provider types, including `anthropic` and `openai`, both of which are compatible with DeepSeek V4 models [docs/deepseek-droid-guide.md94-101](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L94-L101)

 Users can register DeepSeek models within the `customModels` array, specifying parameters such as `maxOutputTokens` (384,000) and `baseUrl` [docs/deepseek-droid-guide.md22-72](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L22-L72) Additionally, the `missionModelSettings` object allows users to designate DeepSeek as the primary `workerModel` or `validationWorkerModel` for autonomous tasks [docs/deepseek-droid-guide.md78-87](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L78-L87)

 **Droid Configuration Structure**

 
```

```

 **Sources:** [docs/deepseek-droid-guide.md18-87](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L18-L87)

 For details on the `customModels` schema and troubleshooting model visibility, see [Factory AI Droid](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/6.2-factory-ai-droid).

 **Sources:** [docs/deepseek-droid-guide.md1-101](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-droid-guide.md?plain=1#L1-L101)
