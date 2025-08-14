LaunchAgents for Mem0 services

This folder contains launchd agent templates for macOS to auto-start the Mem0 MCP server and dependent services at login.

Do NOT load these templates directly. Instead, use the installer script at scripts/install_launch_agents.sh which will:
- Prompt for your repository absolute path
- Substitute correct paths in the templates
- Install them to ~/Library/LaunchAgents
- Load and start them with launchctl
- Provide troubleshooting guidance and log locations

Templates:
- com.gabriel.mem0-apple-intelligence.template.plist
- com.gabriel.mem0-services.template.plist

Logs:
- /tmp/mem0-apple-intelligence.log
- /tmp/mem0-apple-intelligence-error.log
- /tmp/mem0-services.log
- /tmp/mem0-services-error.log
