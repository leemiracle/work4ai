<p align="center">
  <a href="https://browser-use.com" target="_blank">
    <img src="https://avatars.githubusercontent.com/u/192012301?v=4" alt="Browser Use" width="120" height="120">
  </a>
</p>

# Official Browser Use integration for Vercel eve

[![npm version](https://img.shields.io/npm/v/@browser_use/eve.svg)](https://www.npmjs.com/package/@browser_use/eve)
[![npm downloads](https://img.shields.io/npm/dm/@browser_use/eve.svg)](https://www.npmjs.com/package/@browser_use/eve)

> Give a Vercel [eve](https://eve.dev) agent a [Browser Use](https://browser-use.com) cloud browser, in one install — so it can browse, scrape, click, and screenshot the live web, and you can watch it via a liveUrl.

## Compatibility

Requires eve `>=0.11` and Node `>=20`. Ships with `browser-use-sdk`; `eve` and `zod` are peer dependencies.

## Installation

Install the package and scaffold the integration into your eve app:

```sh
npm i @browser_use/eve
npx browser-use-eve add
```

Then add your [Browser Use](https://browser-use.com) API key:

```sh
# .env.local
BROWSER_USE_API_KEY=bu_...
```

That's it — ask your agent to "open example.com and tell me the title."

## Custom Usage

`add` writes four thin files into your eve app. They're one-line re-exports, so the
logic stays in the package and `npm update` ships fixes:

```ts
// agent/sandbox/sandbox.ts
import { browserUseSandbox } from "@browser_use/eve/sandbox";
export default browserUseSandbox();

// agent/skills/browser-use.ts
export { default } from "@browser_use/eve/skill";

// agent/tools/open_cloud_browser.ts
export { default } from "@browser_use/eve/tools/open-cloud-browser";

// agent/tools/stop_cloud_browser.ts
export { default } from "@browser_use/eve/tools/stop-cloud-browser";
```

## How it works

Hardened by default — your API key never leaves the app runtime:

1. `open_cloud_browser` provisions a cloud browser via `browser-use-sdk` and resolves its WebSocket URL.
2. Only that scoped URL is handed to the eve sandbox.
3. The agent drives the browser with `browser-harness-js` (raw, typed Chrome DevTools Protocol).
4. `stop_cloud_browser` ends the cloud browser to stop billing.

## Links

- [Browser Use](https://browser-use.com)
- [Browser Use docs](https://docs.browser-use.com)
- [Vercel eve](https://eve.dev)
