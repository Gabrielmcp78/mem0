#!/usr/bin/env python3
"""
Update all ports to 10000+ range
Systematically updates all configuration files and scripts
"""

import os
import re
import json
from pathlib import Path

class PortUpdater:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.port_mapping = {
            # Old port -> New port
            '3000': '13000',  # OpenMemory UI
            '3001': '13001',  # Enhanced UI
            '6333': '16333',  # Qdrant HTTP
            '6334': '16334',  # Qdrant gRPC
            '7474': '17474',  # Neo4j HTTP
            '7687': '17687',  # Neo4j Bolt
            '8765': '18765',  # OpenMemory MCP API
            '8766': '18766',  # Custom MCP Server
            '8767': '18767',  # Enhanced API Server
            '6379': '16379',  # Redis
            '5432': '15432',  # PostgreSQL
        }
        
        # Files to update
        self.files_to_update = [
            'docker-compose.production.yml',
            'memory_config.yaml',
            'custom_memory_ui/package.json',
            'custom_memory_ui/next.config.js',
            'custom_memory_api/enhanced_api_server.py',
            'mcp_integration_system.py',
            'start_enhanced_system.sh',
            'stop_enhanced_system.sh',
            'test_mem0_final.py',
            'demo_memory_system.py',
            'enhanced_memory_dashboard.tsx',
            'mobile_memory_app.tsx',
            'FINAL_SYSTEM_SUMMARY.md',
            'ENHANCED_README.md',
            'CUSTOMIZATION_PLAN.md',
            'setup_production_memory.py',
            'memory_config_manager.py',
            'agent_memory_integrations.py'
        ]
    
    def log(self, message):
        print(f"🔧 {message}")
    
    def update_file_ports(self, file_path):
        """Update ports in a single file"""
        if not file_path.exists():
            self.log(f"Skipping {file_path} (not found)")
            return
        
        try:
            content = file_path.read_text()
            original_content = content
            
            # Update each port mapping
            for old_port, new_port in self.port_mapping.items():
                # Update various port patterns
                patterns = [
                    f':{old_port}',           # :3000
                    f'port {old_port}',       # port 3000
                    f'port: {old_port}',      # port: 3000
                    f'port={old_port}',       # port=3000
                    f'PORT={old_port}',       # PORT=3000
                    f'localhost:{old_port}',  # localhost:3000
                    f'127.0.0.1:{old_port}', # 127.0.0.1:3000
                    f'0.0.0.0:{old_port}',    # 0.0.0.0:3000
                    f'"{old_port}"',          # "3000"
                    f"'{old_port}'",          # '3000'
                    f'-p {old_port}',         # -p 3000
                ]
                
                replacements = [
                    f':{new_port}',
                    f'port {new_port}',
                    f'port: {new_port}',
                    f'port={new_port}',
                    f'PORT={new_port}',
                    f'localhost:{new_port}',
                    f'127.0.0.1:{new_port}',
                    f'0.0.0.0:{new_port}',
                    f'"{new_port}"',
                    f"'{new_port}'",
                    f'-p {new_port}',
                ]
                
                for pattern, replacement in zip(patterns, replacements):
                    content = content.replace(pattern, replacement)
            
            # Special handling for specific file types
            if file_path.name == 'package.json':
                # Update npm scripts with new ports
                content = re.sub(r'next dev -p \d+', f'next dev -p {self.port_mapping["3001"]}', content)
                content = re.sub(r'next start -p \d+', f'next start -p {self.port_mapping["3001"]}', content)
            
            if content != original_content:
                file_path.write_text(content)
                self.log(f"✅ Updated {file_path}")
            else:
                self.log(f"⚪ No changes needed in {file_path}")
                
        except Exception as e:
            self.log(f"❌ Error updating {file_path}: {e}")
    
    def update_docker_compose(self):
        """Special handling for docker-compose files"""
        compose_file = self.base_dir / 'docker-compose.production.yml'
        if not compose_file.exists():
            return
        
        content = compose_file.read_text()
        
        # Update port mappings in docker-compose format
        port_updates = {
            '"6333:6333"': f'"{self.port_mapping["6333"]}:6333"',
            '"6334:6334"': f'"{self.port_mapping["6334"]}:6334"',
            '"7474:7474"': f'"{self.port_mapping["7474"]}:7474"',
            '"7687:7687"': f'"{self.port_mapping["7687"]}:7687"',
            '"8765:8765"': f'"{self.port_mapping["8765"]}:8765"',
            '"3000:3000"': f'"{self.port_mapping["3000"]}:3000"',
            '"6379:6379"': f'"{self.port_mapping["6379"]}:6379"',
            '"5432:5432"': f'"{self.port_mapping["5432"]}:5432"',
        }
        
        for old_mapping, new_mapping in port_updates.items():
            content = content.replace(old_mapping, new_mapping)
        
        compose_file.write_text(content)
        self.log(f"✅ Updated Docker Compose port mappings")
    
    def update_memory_config(self):
        """Update memory configuration with new ports"""
        config_file = self.base_dir / 'memory_config.yaml'
        if not config_file.exists():
            return
        
        content = config_file.read_text()
        
        # Update Qdrant port
        content = re.sub(r'port: 6333', f'port: {self.port_mapping["6333"]}', content)
        content = re.sub(r'host: localhost\nport: 6333', f'host: localhost\nport: {self.port_mapping["6333"]}', content)
        
        # Update Neo4j URI
        content = re.sub(r'bolt://localhost:7687', f'bolt://localhost:{self.port_mapping["7687"]}', content)
        
        config_file.write_text(content)
        self.log(f"✅ Updated memory configuration")
    
    def create_port_reference(self):
        """Create a port reference file"""
        port_reference = f"""# Port Reference - Updated to 10000+ Range

## New Port Assignments

| Service | Old Port | New Port | Purpose |
|---------|----------|----------|---------|
| OpenMemory UI | 3000 | {self.port_mapping['3000']} | Original OpenMemory interface |
| Enhanced UI | 3001 | {self.port_mapping['3001']} | Modern, accessible interface |
| Qdrant HTTP | 6333 | {self.port_mapping['6333']} | Vector database HTTP API |
| Qdrant gRPC | 6334 | {self.port_mapping['6334']} | Vector database gRPC API |
| Neo4j HTTP | 7474 | {self.port_mapping['7474']} | Graph database web interface |
| Neo4j Bolt | 7687 | {self.port_mapping['7687']} | Graph database Bolt protocol |
| OpenMemory API | 8765 | {self.port_mapping['8765']} | OpenMemory MCP REST API |
| Custom MCP Server | 8766 | {self.port_mapping['8766']} | WebSocket MCP protocol |
| Enhanced API | 8767 | {self.port_mapping['8767']} | Custom API with extensions |
| Redis | 6379 | {self.port_mapping['6379']} | Caching and session storage |
| PostgreSQL | 5432 | {self.port_mapping['5432']} | Structured data storage |

## Updated Access Points

- **Enhanced UI**: http://localhost:{self.port_mapping['3001']}
- **Original UI**: http://localhost:{self.port_mapping['3000']}
- **Enhanced API**: http://localhost:{self.port_mapping['8767']}
- **OpenMemory API**: http://localhost:{self.port_mapping['8765']}
- **MCP WebSocket**: ws://localhost:{self.port_mapping['8766']}
- **Qdrant Dashboard**: http://localhost:{self.port_mapping['6333']}/dashboard
- **Neo4j Browser**: http://localhost:{self.port_mapping['7474']}

## Configuration Updates

All configuration files have been updated to use the new port ranges:
- Docker Compose files
- Memory configuration
- UI package.json
- API server configurations
- MCP server settings
- Test and demo scripts
- Documentation files

## Why 10000+ Range?

- Avoids conflicts with common development ports (3000-9999)
- Follows enterprise port allocation practices
- Reduces chance of port conflicts with other services
- Maintains logical grouping (13xxx for UI, 16xxx for databases, 18xxx for APIs)
"""
        
        with open(self.base_dir / 'PORT_REFERENCE.md', 'w') as f:
            f.write(port_reference)
        
        self.log("✅ Created PORT_REFERENCE.md")
    
    def update_all_files(self):
        """Update all files with new port configurations"""
        self.log("🚀 Starting port update to 10000+ range...")
        
        # Update docker-compose first
        self.update_docker_compose()
        
        # Update memory config
        self.update_memory_config()
        
        # Update all other files
        for file_path in self.files_to_update:
            full_path = self.base_dir / file_path
            self.update_file_ports(full_path)
        
        # Create port reference
        self.create_port_reference()
        
        self.log("🎉 Port update complete!")
        self.log("")
        self.log("📍 New access points:")
        self.log(f"  Enhanced UI:     http://localhost:{self.port_mapping['3001']}")
        self.log(f"  Original UI:     http://localhost:{self.port_mapping['3000']}")
        self.log(f"  Enhanced API:    http://localhost:{self.port_mapping['8767']}")
        self.log(f"  OpenMemory API:  http://localhost:{self.port_mapping['8765']}")
        self.log(f"  MCP Server:      ws://localhost:{self.port_mapping['8766']}")
        self.log(f"  Qdrant:          http://localhost:{self.port_mapping['6333']}")
        self.log(f"  Neo4j:           http://localhost:{self.port_mapping['7474']}")
        self.log("")
        self.log("📚 See PORT_REFERENCE.md for complete details")

if __name__ == "__main__":
    updater = PortUpdater()
    updater.update_all_files()