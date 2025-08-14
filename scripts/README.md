# Scripts

## install_launch_agents.sh
Installs the launchd agents from launch_agents/* templates by substituting ${REPO_PATH} and loading them. Auto-detects the current repo path or allows you to specify a custom one.

**Usage:**
```bash
bash scripts/install_launch_agents.sh
```

**What it does:**
- Auto-detects current repository path
- Validates required files exist (start_mem0_services.sh, MCP server)
- Substitutes ${REPO_PATH} placeholders in template files
- Installs to ~/Library/LaunchAgents/
- Loads the agents with launchctl

**After install:**
- Check status: `launchctl list | grep mem0`
- View logs: `tail -f /tmp/mem0-*.log`
- Test setup: `bash scripts/test_launch_agents.sh`

## test_launch_agents.sh
Tests the launch agent setup and verifies services are running correctly.

**Usage:**
```bash
bash scripts/test_launch_agents.sh
```

**What it checks:**
- Launch agent files exist
- Agents are loaded in launchctl
- Recent log entries
- Docker containers are running
- Service ports are responding (Qdrant, Neo4j)

## verify_setup.sh
Comprehensive verification of the entire Mem0 FoundationModels setup.

**Usage:**
```bash
bash scripts/verify_setup.sh
```

**What it verifies:**
- System requirements (macOS version, Apple Silicon)
- Dependencies (Python packages, Node.js modules)
- FoundationModels availability
- Service health (Docker, Qdrant, Neo4j)
- Launch agent installation and status
- Required files and permissions

**Exit codes:**
- 0: All checks passed
- 1: Most checks passed (minor issues)
- 2: Many checks failed (needs attention)

## Troubleshooting

**If agents fail to start:**
1. Check logs in /tmp/mem0-*.log
2. Verify paths in plist files are correct
3. Ensure Docker is running
4. Test manually: `bash start_mem0_services.sh`

**To reload agents:**
```bash
launchctl unload ~/Library/LaunchAgents/com.gabriel.mem0-*.plist
launchctl load -w ~/Library/LaunchAgents/com.gabriel.mem0-*.plist
```
