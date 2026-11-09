# Install and test Agent Entrepreneur

## ChatGPT desktop app / Codex local marketplace

1. Clone this repository and open it as a trusted project in the ChatGPT desktop app or Codex environment.
2. The repository includes a local marketplace at .agents/plugins/marketplace.json that points to plugins/agent-entrepreneur.
3. Restart the ChatGPT desktop app if the marketplace is not detected.
4. Open Plugins, select the Agent Entrepreneur marketplace, and install Agent Entrepreneur.
5. Start a new chat and test the included workflows using the starter prompts in the manifest.

Local marketplace availability depends on the host surface and account/workspace settings. A local install is for development and private distribution; it does not publish the Plugin to the public directory.

## Public Plugin Directory

For public distribution, prepare the exact package and submit it through the OpenAI Platform Plugin submission portal. A public listing requires verified developer identity, public legal/support URLs, five positive and three negative reviewer cases, successful package checks and OpenAI review. Approval and a separate publish action are required before public availability.

## Separate Python/MCP distribution

The Plugin is Skills-only. To use the separate local MCP server, follow the installation and client-setup instructions in the repository README and docs/client-setup.md. The MCP server is not bundled in this Plugin and must not be exposed publicly without a separate authenticated production deployment and security review.
