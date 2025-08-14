#!/bin/bash

# Create the bin directory and executable for apple-intelligence-dxt
DXT_DIR="/Volumes/Ready500/DEVELOPMENT/DXT-AppleIntel"
BIN_DIR="$DXT_DIR/bin"
BINARY_PATH="$BIN_DIR/apple-intelligence-dxt"

echo "Creating apple-intelligence-dxt binary..."

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# Create the executable binary
cat > "$BINARY_PATH" << 'EOF'
#!/usr/bin/env node

// Apple Intelligence DXT MCP Server Binary
// This is the main entry point for the MCP server

const path = require('path');
const { spawn } = require('child_process');

// Get the directory where this binary is located
const binDir = __dirname;
const projectDir = path.dirname(binDir);
const serverScript = path.join(projectDir, 'dist', 'index.js');

// Check if the server script exists
const fs = require('fs');
if (!fs.existsSync(serverScript)) {
    console.error(`Error: Server script not found at ${serverScript}`);
    console.error('Please run "npm run build" to build the project first.');
    process.exit(1);
}

// Start the server
const server = spawn('node', [serverScript], {
    stdio: 'inherit',
    cwd: projectDir,
    env: {
        ...process.env,
        NODE_ENV: process.env.NODE_ENV || 'production'
    }
});

server.on('error', (err) => {
    console.error('Failed to start apple-intelligence-dxt server:', err);
    process.exit(1);
});

server.on('close', (code) => {
    process.exit(code);
});

// Handle signals
process.on('SIGINT', () => {
    server.kill('SIGINT');
});

process.on('SIGTERM', () => {
    server.kill('SIGTERM');
});
EOF

# Make the binary executable
chmod +x "$BINARY_PATH"

echo "Binary created at: $BINARY_PATH"
echo "Testing binary..."

# Test if the binary works
if [ -f "$BINARY_PATH" ]; then
    echo "✅ Binary created successfully"
    echo "You can now test it with: $BINARY_PATH"
else
    echo "❌ Failed to create binary"
    exit 1
fi