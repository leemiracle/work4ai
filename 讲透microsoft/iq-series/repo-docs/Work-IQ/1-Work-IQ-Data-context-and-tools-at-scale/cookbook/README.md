# Episode 1 Cookbook: Data, context, and tools at scale

This folder contains the hands-on cookbook for Episode 1 of The Work IQ Series.

## 📋 Prerequisites

- **Microsoft 365 Tenant** with proper licensing
- **Node.js** 22 or later installed
- **GitHub Copilot CLI** installed
- **Work IQ** enabled in your target tenant with **Administrative consent** for the **Work IQ application**
- **Work IQ CLI** installed

## 🛠️ Installing GitHub Copilot CLI

GitHub Copilot CLI is available with all Copilot plans and provides a command-line interface to interact with GitHub Copilot. Choose the installation method that works best for your platform:

### Prerequisites

Before installing GitHub Copilot CLI, ensure you have:

- An active GitHub Copilot subscription
- Node.js 22 or later (for npm installation)
- PowerShell v6 or higher (on Windows)

> **Note:** If you have access to GitHub Copilot through your organization, make sure your organization has enabled Copilot CLI in their settings.

### Installation Methods

#### Option 1: Using npm (All Platforms)

```bash
npm install -g @github/copilot
```

If you have `ignore-scripts=true` in your `~/.npmrc` file, use:

```bash
npm_config_ignore_scripts=false npm install -g @github/copilot
```

To install the prerelease version:

```bash
npm install -g @github/copilot@prerelease
```

#### Option 2: Using WinGet (Windows)

```powershell
winget install GitHub.Copilot
```

To install the prerelease version:

```powershell
winget install GitHub.Copilot.Prerelease
```

#### Option 3: Using Homebrew (macOS and Linux)

```bash
brew install copilot-cli
```

To install the prerelease version:

```bash
brew install copilot-cli@prerelease
```

#### Option 4: Using Install Script (macOS and Linux)

```bash
curl -fsSL https://gh.io/copilot-install | bash
```

Or using wget:

```bash
wget -qO- https://gh.io/copilot-install | bash
```

To install to a custom directory, set the `PREFIX` environment variable:

```bash
curl -fsSL https://gh.io/copilot-install | PREFIX="$HOME/custom" bash
```

#### Option 5: Download from GitHub

Download the executable directly from the [copilot-cli repository](https://github.com/github/copilot-cli/releases/). Then unpack and run the executable for your platform.

### Authentication

On first launch, you'll be prompted to authenticate. Use the `/login` slash command and follow the on-screen instructions to log in with your GitHub account.

Alternatively, you can authenticate using a fine-grained personal access token with the "Copilot Requests" permission by exporting it as an environment variable:

```bash
export COPILOT_GITHUB_TOKEN=<your_token>
# or
export GH_TOKEN=<your_token>
# or
export GITHUB_TOKEN=<your_token>
```

### Learn More

For a comprehensive beginner's guide to using GitHub Copilot CLI, visit the [GitHub Copilot CLI for Beginners](https://github.com/github/copilot-cli-for-beginners/) repository.

## ⚙️ Enabling Work IQ in your tenant

Follow this brief enablement flow as a tenant admin:

1. Verify licensing requirements are satisfied for users who need Work IQ. You can find additional details about the licensing model in the article [Understand usage-based billing and cost management for Copilot Credits](https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-overview-copilot-credits)
1. Ensure you have a **Global Administrator** role in your organization.
1. Create the Work IQ service principal in your organization using one of these methods:

   **Option A: Using Graph Explorer (Admin center)**
   - Go to [Graph Explorer](https://aka.ms/ge) and sign in with an admin account.
   - Set the method to **POST** and the URL to `https://graph.microsoft.com/v1.0/servicePrincipals`.
   - Select **Modify permissions** and consent to `Application.ReadWrite.All`.
   - Enter the following in the **Request body**:
     ```json
     {
       "appId": "fdcc1f02-fc51-4226-8753-f668596af7f7"
     }
     ```
   - Select **Run query**. A **201 Created** response confirms success.

   **Option B: Using Azure CLI**
   ```bash
   az ad sp create --id fdcc1f02-fc51-4226-8753-f668596af7f7
   ```

Your tenant is now ready to use Work IQ. For complete prerequisites, detailed instructions, and troubleshooting, see the [full Work IQ enablement guide](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/enable-work-iq).

## 🏗️ Installing Work IQ CLI

Work IQ CLI can be installed in multiple ways depending on your setup. Choose the method that best fits your workflow:

### Option 1: Using GitHub Copilot CLI (Recommended)

The fastest way to get started:

```bash
# Open GitHub Copilot CLI
copilot

# Add the plugins marketplace (one-time setup)
/plugin marketplace add github/copilot-plugins

# Install Work IQ
/plugin install workiq@copilot-plugins

# Restart Copilot CLI
```

### Option 2: Install Globally

Install Work IQ globally using npm:

```bash
npm install -g @microsoft/workiq
```

### Option 3: Run with npx (No Installation Required)

Use Work IQ directly without installation:

```bash
npx -y @microsoft/workiq mcp
```

### Option 4: Install in VS Code

Click one of these links to add Work IQ as an MCP server in VS Code:

- [Install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40microsoft%2Fworkiq%22%2C%22mcp%22%5D%2C%22name%22%3A%22workiq%22%7D)
- [Install in VS Code Insiders](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40microsoft%2Fworkiq%22%2C%22mcp%22%5D%2C%22name%22%3A%22workiq%22%7D)

### Option 5: Manual MCP Configuration

Add the following configuration to your MCP settings file:

```json
{
  "workiq": {
    "command": "npx",
    "args": [
      "-y",
      "@microsoft/workiq",
      "mcp"
    ],
    "tools": [
      "*"
    ]
  }
}
```

### Accept the End User License Agreement

Before using Work IQ for the first time, accept the EULA:

```bash
workiq accept-eula
```

### Prerequisites

Before installing, ensure you have:

- Node.js installed on your machine
- A Microsoft 365 subscription with a Copilot license and Copilot Credits configured
- Administrative consent for the Work IQ application in your Microsoft Entra tenant
- GitHub Copilot CLI (optional, but recommended)

> **Note:** To access Microsoft 365 organization data, the Work IQ CLI needs administrative consent in your organization. If you're not an organization administrator, contact your admin for access.

### Platform Support

Work IQ supports:
- Windows (x64 and ARM64)
- Linux (x64 and ARM64)
- macOS (x64 and ARM64)
- Windows Subsystem for Linux (WSL) with browser support

For more information, see the [Work IQ CLI documentation](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq-cli).

## 📓 Lab Instructions

The [**Work IQ Lab for Episode 01**](./work-iq-lab01.md) walks you through the basic capabilities of Work IQ, step by step:

1. Asking a prompt via Work IQ CLI
1. Asking a prompt via GitHub Copilot CLI
1. Making a REST request to Work IQ API

## Additional Resources

- [Episode 1 README](../README.md)
- [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq)
- [Copilot Dev Camp - Work IQ](https://microsoft.github.io/copilot-camp/pages/work-iq/)
