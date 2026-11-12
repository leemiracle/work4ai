<!-- source: DeepWiki mcp.deepwiki.com · repo botpress/botpress · page 8 Example Bots · fetched 2026-10-27 -->

# Example Bots

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Tiltfile](Tiltfile)
- [bots/bugbuster/bot.definition.ts](bots/bugbuster/bot.definition.ts)
- [bots/bugbuster/package.json](bots/bugbuster/package.json)
- [bots/bugbuster/src/bootstrap.ts](bots/bugbuster/src/bootstrap.ts)
- [bots/bugbuster/src/handlers/github-issue-opened.ts](bots/bugbuster/src/handlers/github-issue-opened.ts)
- [bots/bugbuster/src/handlers/index.ts](bots/bugbuster/src/handlers/index.ts)
- [bots/bugbuster/src/handlers/linear-issue-created.ts](bots/bugbuster/src/handlers/linear-issue-created.ts)
- [bots/bugbuster/src/handlers/linear-issue-updated.ts](bots/bugbuster/src/handlers/linear-issue-updated.ts)
- [bots/bugbuster/src/handlers/lint-all.ts](bots/bugbuster/src/handlers/lint-all.ts)
- [bots/bugbuster/src/handlers/message-created.ts](bots/bugbuster/src/handlers/message-created.ts)
- [bots/bugbuster/src/handlers/time-to-check-issues-state.ts](bots/bugbuster/src/handlers/time-to-check-issues-state.ts)
- [bots/bugbuster/src/index.ts](bots/bugbuster/src/index.ts)
- [bots/bugbuster/src/services/command-processor.ts](bots/bugbuster/src/services/command-processor.ts)
- [bots/bugbuster/src/services/issue-processor/index.ts](bots/bugbuster/src/services/issue-processor/index.ts)
- [bots/bugbuster/src/services/issue-processor/lint-issue.ts](bots/bugbuster/src/services/issue-processor/lint-issue.ts)
- [bots/bugbuster/src/services/issue-state-checker.ts](bots/bugbuster/src/services/issue-state-checker.ts)
- [bots/bugbuster/src/services/recently-linted-manager.ts](bots/bugbuster/src/services/recently-linted-manager.ts)
- [bots/bugbuster/src/services/teams-manager.ts](bots/bugbuster/src/services/teams-manager.ts)
- [bots/bugbuster/src/types.ts](bots/bugbuster/src/types.ts)
- [bots/bugbuster/src/utils/botpress-utils.ts](bots/bugbuster/src/utils/botpress-utils.ts)
- [bots/bugbuster/src/utils/linear-utils/client.ts](bots/bugbuster/src/utils/linear-utils/client.ts)
- [bots/bugbuster/src/utils/linear-utils/graphql-queries.ts](bots/bugbuster/src/utils/linear-utils/graphql-queries.ts)
- [bots/clog/bot.definition.ts](bots/clog/bot.definition.ts)
- [bots/clog/package.json](bots/clog/package.json)
- [bots/clog/src/index.ts](bots/clog/src/index.ts)
- [bots/hello-world/bot.definition.ts](bots/hello-world/bot.definition.ts)
- [bots/hello-world/package.json](bots/hello-world/package.json)
- [bots/hello-world/src/index.ts](bots/hello-world/src/index.ts)
- [bots/hit-looper/package.json](bots/hit-looper/package.json)
- [bots/knowledgiani/bot.definition.ts](bots/knowledgiani/bot.definition.ts)
- [bots/sheetzy/bot.definition.ts](bots/sheetzy/bot.definition.ts)
- [bots/sheetzy/package.json](bots/sheetzy/package.json)
- [bots/sheetzy/src/index.ts](bots/sheetzy/src/index.ts)
- [bots/sheetzy/src/types.ts](bots/sheetzy/src/types.ts)
- [bots/sinlin/bot.definition.ts](bots/sinlin/bot.definition.ts)
- [bots/sinlin/package.json](bots/sinlin/package.json)
- [bots/sinlin/src/index.ts](bots/sinlin/src/index.ts)
- [bots/slackbox/bot.definition.ts](bots/slackbox/bot.definition.ts)
- [bots/slackbox/eslint.config.mjs](bots/slackbox/eslint.config.mjs)
- [bots/slackbox/package.json](bots/slackbox/package.json)
- [bots/slackbox/src/index.ts](bots/slackbox/src/index.ts)
- [bots/slackbox/tsconfig.json](bots/slackbox/tsconfig.json)
- [integrations/asana/package.json](integrations/asana/package.json)
- [integrations/mailchimp/package.json](integrations/mailchimp/package.json)
- [integrations/stripe/package.json](integrations/stripe/package.json)
- [integrations/teams/package.json](integrations/teams/package.json)
- [integrations/todoist/package.json](integrations/todoist/package.json)
- [integrations/whatsapp/package.json](integrations/whatsapp/package.json)
- [integrations/whatsapp/src/index.ts](integrations/whatsapp/src/index.ts)
- [integrations/zendesk/package.json](integrations/zendesk/package.json)
- [packages/sdk-addons/package.json](packages/sdk-addons/package.json)

</details>



This page provides a high-level overview of the reference bot implementations located in the `bots/` directory of the Botpress monorepo. These examples serve as practical demonstrations of how to build various types of bots using the Botpress SDK and integrate with different external services. Each bot showcases specific features and integration patterns, ranging from simple conversational agents to complex automation workflows.

The `bots/` directory contains several examples, each designed to illustrate different aspects of the Botpress platform:
- **Bugbuster**: An advanced bot for automated GitHub/Linear issue triage.
- **Hello-World**: A minimal bot template to get started with Botpress.
- **HIT-Looper**: A bot designed for Human-in-the-Loop (HITL) testing.
- **Sheetzy**: A bot that interacts with Google Sheets.
- **Slackbox**: A bot demonstrating Slack integration capabilities.
- **Sinlin**: A bot showcasing integration with Linear.
- **Knowledgiani**: A bot focused on knowledge base interactions.
- **Synchrotron**: Another example bot.
- **Clog**: A bot for monitoring Meta API versions.

For detailed information on each specific bot, please refer to their respective child pages.

Sources:
- [bots/bugbuster/package.json]()
- [bots/hello-world/package.json]()
- [bots/hit-looper/package.json]()
- [bots/sheetzy/package.json]()
- [bots/slackbox/package.json]()
- [bots/sinlin/package.json]()
- [bots/knowledgiani/bot.definition.ts]()
- [bots/clog/package.json]()

## Bugbuster Bot

The Bugbuster bot is a sophisticated example demonstrating automated issue triage for GitHub and Linear. It leverages Large Language Models (LLMs) for intelligent processing, handles command-line interactions, implements a lint-issue pipeline, manages teams, and integrates seamlessly with the Linear and GitHub integrations. This bot is a prime example of building an intelligent automation agent within the Botpress ecosystem.

The `bot.definition.ts` file for Bugbuster defines its states, workflows, events, and recurring events, along with its integrations. For instance, it defines `watchedTeams` and `notificationChannels` as bot-level states, and `lintAll` as a workflow [bots/bugbuster/bot.definition.ts:14-72](). It also sets up recurring events like `timeToLintAll` and `timeToCheckIssuesState` [bots/bugbuster/bot.definition.ts:83-96](). The bot integrates with GitHub, Telegram, Linear, and Slack, configuring their respective tokens and settings [bots/bugbuster/bot.definition.ts:102-136]().

The bot's core logic is handled by various event listeners defined in `src/index.ts`. It listens for GitHub and Linear issue events, as well as internal `timeToLintAll` and `timeToCheckIssuesState` events. It also processes messages from users via the `handleMessageCreated` handler [bots/bugbuster/src/index.ts:6-11](). Workflows like `lintAll` are managed with `on.workflowStart`, `on.workflowContinue`, and `on.workflowTimeout` handlers [bots/bugbuster/src/index.ts:13-15]().

The `handleMessageCreated` handler [bots/bugbuster/src/handlers/message-created.ts:7-61]() is responsible for parsing user commands and executing them. It supports commands for managing watched teams, adding/removing notification channels, and triggering the `lintAll` workflow. The `CommandProcessor` class [bots/bugbuster/src/services/command-processor.ts:7-231]() encapsulates the logic for these commands, interacting with Botpress states and integration actions.

For details, see [Bugbuster Bot](#8.1).

Sources:
- [bots/bugbuster/bot.definition.ts:14-72]()
- [bots/bugbuster/bot.definition.ts:83-96]()
- [bots/bugbuster/bot.definition.ts:102-136]()
- [bots/bugbuster/src/index.ts:6-11]()
- [bots/bugbuster/src/index.ts:13-15]()
- [bots/bugbuster/src/handlers/message-created.ts:7-61]()
- [bots/bugbuster/src/services/command-processor.ts:7-231]()

## Other Reference Bots

Beyond Bugbuster, the `bots/` directory includes several other reference implementations, each serving a unique purpose and demonstrating different Botpress capabilities.

### Hello-World Bot

The Hello-World bot is the simplest possible Botpress bot, serving as a minimal template for new projects. It demonstrates basic bot registration and message handling. The `bot.definition.ts` defines a single action `sayHello` [bots/hello-world/bot.definition.ts:8-17]() and integrates with Telegram and a generic chat integration [bots/hello-world/bot.definition.ts:20-30](). The `src/index.ts` file shows how to register the bot and respond to any incoming message by calling the `sayHello` action and sending its output back to the user [bots/hello-world/src/index.ts:3-28]().

Sources:
- [bots/hello-world/bot.definition.ts:8-17]()
- [bots/hello-world/bot.definition.ts:20-30]()
- [bots/hello-world/src/index.ts:3-28]()

### HIT-Looper Bot

The HIT-Looper bot is designed as a harness for Human-in-the-Loop (HITL) testing. It facilitates scenarios where human intervention is required to validate or assist bot conversations, which is crucial for developing robust conversational AI systems.

Sources:
- [bots/hit-looper/package.json]()

### Sheetzy Bot

Sheetzy is an example bot that demonstrates integration with Google Sheets. It showcases how to read from and write to Google Sheets, enabling bots to interact with structured data stored in spreadsheets. This is useful for tasks like data entry, reporting, or dynamic content retrieval.

Sources:
- [bots/sheetzy/package.json]()
- [bots/sheetzy/bot.definition.ts]()
- [bots/sheetzy/src/index.ts]()
- [bots/sheetzy/src/types.ts]()

### Slackbox Bot

The Slackbox bot provides a comprehensive example of integrating a Botpress bot with Slack. It covers various aspects of Slack interaction, such as sending messages, handling events, and utilizing Slack-specific features.

Sources:
- [bots/slackbox/package.json]()
- [bots/slackbox/bot.definition.ts]()
- [bots/slackbox/src/index.ts]()
- [bots/slackbox/tsconfig.json]()
- [bots/slackbox/eslint.config.mjs]()

### Sinlin Bot

Sinlin is a bot that integrates with Linear, a popular issue tracking tool. It demonstrates how to interact with Linear's API to manage issues, projects, and teams, similar to some functionalities in the Bugbuster bot but potentially focusing on different use cases or simpler interactions.

Sources:
- [bots/sinlin/package.json]()
- [bots/sinlin/bot.definition.ts]()
- [bots/sinlin/src/index.ts]()

### Knowledgiani Bot

The Knowledgiani bot focuses on knowledge base interactions. It illustrates how a bot can retrieve, process, and respond with information from a knowledge base, which is fundamental for building informative and helpful conversational agents.

Sources:
- [bots/knowledgiani/bot.definition.ts]()

### Clog Bot

The Clog bot is designed to monitor Meta API versions. It defines a bot-level state `metaApiVersions` to store the current Graph API version [bots/clog/bot.definition.ts:5-15]() and uses a recurring event `timeToCheckApi` to periodically check for updates [bots/clog/bot.definition.ts:17-27](). It integrates with Slack to potentially send notifications about API changes [bots/clog/bot.definition.ts:29-40]().

Sources:
- [bots/clog/bot.definition.ts:5-15]()
- [bots/clog/bot.definition.ts:17-27]()
- [bots/clog/bot.definition.ts:29-40]()
- [bots/clog/package.json]()
- [bots/clog/src/index.ts]()

For details, see [Other Reference Bots](#8.2).

---

