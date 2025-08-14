#!/usr/bin/env bash
set -euo pipefail

TEMPLATES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/launch_agents"
DEST_DIR="$HOME/Library/LaunchAgents"

# Auto-detect current repo path or prompt user
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Auto-detected repo path: $CURRENT_DIR"
read -rp "Press Enter to use this path, or enter a different absolute path: " USER_PATH

if [[ -n "$USER_PATH" ]]; then
  REPO_PATH="$USER_PATH"
else
  REPO_PATH="$CURRENT_DIR"
fi

if [[ ! -d "$REPO_PATH" ]]; then
  echo "Path does not exist: $REPO_PATH" >&2
  exit 1
fi

# Validate required files exist
if [[ ! -f "$REPO_PATH/start_mem0_services.sh" ]]; then
  echo "Error: start_mem0_services.sh not found in $REPO_PATH" >&2
  exit 1
fi

if [[ ! -f "$REPO_PATH/integrations/mcp/mem0_native_node_server.js" ]]; then
  echo "Error: integrations/mcp/mem0_native_node_server.js not found in $REPO_PATH" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

echo "Installing launch agents to $DEST_DIR"
for tmpl in \
  com.gabriel.mem0-apple-intelligence.template.plist \
  com.gabriel.mem0-services.template.plist; do
  src="$TEMPLATES_DIR/$tmpl"
  dst="$DEST_DIR/${tmpl/.template/}"
  sed "s#\${REPO_PATH}#$REPO_PATH#g" "$src" > "$dst"
  launchctl unload "$dst" >/dev/null 2>&1 || true
  launchctl load -w "$dst"
  echo "Loaded: $(basename "$dst")"
  echo "  Logs: /tmp/$(basename "$dst" .plist).log and -error.log"
  echo
 done

echo "Done. Check logs in /tmp and status with: launchctl list | grep mem0"
