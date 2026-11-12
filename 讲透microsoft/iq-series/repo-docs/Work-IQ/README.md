<h1 align="center">Work IQ</h1>

**Work IQ** is a workplace intelligence layer that delivers a semantic understanding of everything happening across your business. Built on four core components—Chat, Context, Tools, and Workspaces—it continuously transforms signals from across Microsoft 365 and business systems into agent‑ready intelligence, enabling work grounding, reasoning, and permission awareness. The result is a platform purpose-built for agentic use, delivering higher intelligence, speed, efficiency, enterprise scale, and security and governance by design.

This folder contains the Work IQ episodes of The Microsoft IQ Series, including hands-on cookbooks with step-by-step guidance.

> **👉 New here? Start with Episode 1.** Follow the [Get Started](#-get-started) steps below to install the tooling and enable Work IQ in your tenant, then open the [Episode 1 cookbook](./1-Work-IQ-Data-context-and-tools-at-scale/cookbook/) and work through it end-to-end. Episodes build on each other, so working through them in order (1 → 2) gives you the smoothest learning path.

## 📚 Episodes

| **Episode**                                                                                                                          | **Description**                                                                    | **Video**       | **Cookbook**                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|-----------------|-------------------------------------------------------------------------------------|
| [Work IQ: Data, context, and tools at scale](./1-Work-IQ-Data-context-and-tools-at-scale/README.md)                                          | Overview, architecture, and protocol strategy (REST, A2A, MCP) of Work IQ           | [Watch Now 🎥](https://aka.ms/iq-series/work-iq/episode1)     | [Cookbook](./1-Work-IQ-Data-context-and-tools-at-scale/cookbook/)                |
| [Work IQ: A2A for Context‑Aware, Agentic Experiences](./2-Work-IQ-A2A-for-Context‑Aware-Agentic-Experiences/README.md)                        | The A2A (Agent-2-Agent) protocol, discovery, and prototyping with Work IQ A2A       | [Watch Now 🎥](https://aka.ms/iq-series/work-iq/episode2)     | [Cookbook](./2-Work-IQ-A2A-for-Context‑Aware-Agentic-Experiences/cookbook/)      |

## 🚀 Get Started

### 1. Prerequisites

- **Microsoft 365 Tenant** with proper licensing
- **Node.js** 22 or later installed
- **GitHub Copilot CLI** installed (with an active GitHub Copilot subscription)
- **Work IQ** enabled in your target tenant with **administrative consent** for the **Work IQ application**
- **Work IQ CLI** installed

### 2. Install GitHub Copilot CLI

Install the GitHub Copilot CLI using the method that fits your platform:

```bash
# npm (all platforms)
npm install -g @github/copilot

# WinGet (Windows)
winget install GitHub.Copilot

# Homebrew (macOS and Linux)
brew install copilot-cli
```

On first launch, run `copilot` and use the `/login` slash command to authenticate with your GitHub account. For full installation and authentication options, see each episode's cookbook.

### 3. Enable Work IQ in your tenant

As a tenant admin, grant tenant-wide admin consent for the Work IQ application:

1. Sign in with an eligible admin role (e.g., Global Administrator or Application Administrator).
2. Grant admin consent using this URL (replace `{your-tenant-id}` with your tenant ID or domain):
   `https://login.microsoftonline.com/{your-tenant-id}/adminconsent?client_id=ba081686-5d24-4bc6-a0d6-d034ecffed87`
3. If consent returns access-denied/AADSTS errors, run the [enablement script](https://github.com/microsoft/work-iq/blob/main/scripts/Enable-WorkIQToolsForTenant.ps1) to provision missing service principals, then retry consent.

For complete prerequisites, exact URLs/scripts, troubleshooting, and security guidance, see the full [admin guide](https://github.com/microsoft/work-iq/blob/main/ADMIN-INSTRUCTIONS.md).

### 4. Install Work IQ CLI

The fastest way is via the GitHub Copilot CLI plugin marketplace:

```bash
# Open GitHub Copilot CLI
copilot

# Add the plugins marketplace (one-time setup)
/plugin marketplace add github/copilot-plugins

# Install Work IQ
/plugin install workiq@copilot-plugins

# Restart Copilot CLI
```

Alternatively, install globally (`npm install -g @microsoft/workiq`) or run without installing (`npx -y @microsoft/workiq mcp`). Before first use, accept the EULA:

```bash
workiq accept-eula
```

### 5. Run the Cookbooks

Each episode's cookbook lives in its `cookbook/` folder and includes prerequisites, setup, and step-by-step instructions. Start with Episode 1 and work through the episodes in order:

1. [Episode 1 cookbook](./1-Work-IQ-Data-context-and-tools-at-scale/cookbook/) — Data, context, and tools at scale
2. [Episode 2 cookbook](./2-Work-IQ-A2A-for-Context‑Aware-Agentic-Experiences/cookbook/) — A2A for Context‑Aware, Agentic Experiences

## 🔗 Learn More

- 📖 [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq)
- 📚 [Copilot Dev Camp - Work IQ](https://microsoft.github.io/copilot-camp/pages/work-iq/)
- 💬 Ask your questions in our [Discussions](https://aka.ms/iq/discussions)
