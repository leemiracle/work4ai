# Connections and presets

## Presets

A **preset** is a one-click integration template in the admin UI. Selecting a
preset creates the credential, network rule, and (where applicable) MCP server
entries needed for a common integration — without hand-authoring each piece.
Use a preset whenever one exists for the service you're integrating.

## Connections

A **connection** is an authenticated link to an external service.

- **OAuth-based connections** (for example, Google Workspace) walk the admin
  through the provider's consent flow and store the resulting token as a
  credential on the chosen identity profile.
- **MCP connections** attach an MCP server to sessions. Once attached, the
  server's tools become available in any session where that profile applies.

## Installing a connection or preset

1. Open claude.ai → admin settings → **Claude in Slack**.
2. Select the identity profile that should carry the integration.
3. Open **Connections** (or **Presets**) and add the one you need.
4. Complete any provider consent flow if prompted.

The connection takes effect on the **next new session**. Existing Slack threads
keep the configuration they were started with — start a fresh thread to use the
new connection.
