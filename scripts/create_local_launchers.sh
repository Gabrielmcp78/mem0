#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Creating local launchers for launchd compatibility"
echo "===================================================="

REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_SCRIPTS_DIR="$HOME/.mem0-scripts"

# Create local scripts directory
mkdir -p "$LOCAL_SCRIPTS_DIR"

echo "📁 Creating local script wrappers in $LOCAL_SCRIPTS_DIR"

# Create local wrapper for services
cat > "$LOCAL_SCRIPTS_DIR/start_mem0_services.sh" << EOF
#!/usr/bin/env bash
set -euo pipefail

# Set PATH for Docker and other tools
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Applications/Docker.app/Contents/Resources/bin:\$PATH"

# Change to repo directory
cd "$REPO_PATH"

# Execute the actual script
exec bash "$REPO_PATH/start_mem0_services.sh"
EOF

# Create local wrapper for Node.js server
cat > "$LOCAL_SCRIPTS_DIR/start_apple_intelligence_server.sh" << EOF
#!/usr/bin/env bash
set -euo pipefail

# Set PATH for Node.js and other tools
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:\$PATH"

# Set environment variables
export QDRANT_URL="http://localhost:10333"
export QDRANT_COLLECTION="gabriel_apple_intelligence_memories"
export APPLE_INTELLIGENCE_ENABLED="true"
export LOG_LEVEL="INFO"

# Change to repo directory
cd "$REPO_PATH"

# Execute the Node.js server
exec node "$REPO_PATH/integrations/mcp/mem0_native_node_server.cjs"
EOF

# Make scripts executable
chmod +x "$LOCAL_SCRIPTS_DIR/start_mem0_services.sh"
chmod +x "$LOCAL_SCRIPTS_DIR/start_apple_intelligence_server.sh"

echo "✅ Created local launchers:"
echo "   - $LOCAL_SCRIPTS_DIR/start_mem0_services.sh"
echo "   - $LOCAL_SCRIPTS_DIR/start_apple_intelligence_server.sh"

# Update launch agents to use local scripts
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo ""
echo "🔄 Updating launch agents to use local scripts..."

# Update services launch agent
cat > "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-services.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gabriel.mem0-services</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>bash</string>
        <string>$LOCAL_SCRIPTS_DIR/start_mem0_services.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/mem0-services.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/mem0-services-error.log</string>

    <key>WorkingDirectory</key>
    <string>$HOME</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Applications/Docker.app/Contents/Resources/bin</string>
    </dict>
</dict>
</plist>
EOF

# Update FoundationModels launch agent
cat > "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-apple-intelligence.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gabriel.mem0-apple-intelligence</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>bash</string>
        <string>$LOCAL_SCRIPTS_DIR/start_apple_intelligence_server.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>

    <key>ThrottleInterval</key>
    <integer>10</integer>

    <key>WorkingDirectory</key>
    <string>$HOME</string>

    <key>StandardOutPath</key>
    <string>/tmp/mem0-apple-intelligence.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mem0-apple-intelligence-error.log</string>

    <key>SoftResourceLimits</key>
    <dict>
        <key>NumberOfFiles</key>
        <integer>1024</integer>
    </dict>
</dict>
</plist>
EOF

echo "✅ Updated launch agents to use local scripts"

# Reload the agents
echo ""
echo "🔄 Reloading launch agents..."

launchctl unload "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-services.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-apple-intelligence.plist" 2>/dev/null || true

launchctl load -w "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-services.plist"
launchctl load -w "$LAUNCH_AGENTS_DIR/com.gabriel.mem0-apple-intelligence.plist"

echo "✅ Launch agents reloaded"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Check status with:"
echo "  launchctl list | grep mem0"
echo ""
echo "View logs with:"
echo "  tail -f /tmp/mem0-*.log"