#!/usr/bin/env python3
"""
Migration Tool: Managed Mem0 to Local System
Export memories from managed Mem0 service and import to local infrastructure
"""

import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mem0 import Memory
    from mem0.config import Config
except ImportError:
    print("Error: mem0ai package not installed. Install with: pip install mem0ai")
    sys.exit(1)

class Mem0Migrator:
    """Tool for migrating from managed Mem0 to local system"""
    
    def __init__(self, managed_api_key: str, local_config: Optional[Dict] = None):
        self.managed_api_key = managed_api_key
        self.managed_base_url = "https://api.mem0.ai/v1"
        
        # Initialize local memory system
        if local_config:
            config = Config.from_dict(local_config)
            self.local_memory = Memory(config=config)
        else:
            # Default local configuration
            default_config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": "localhost",
                        "port": 26333,
                        "collection_name": "migrated_memories"
                    }
                },
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": "llama3.2:3b",
                        "base_url": "http://localhost:11434"
                    }
                }
            }
            config = Config.from_dict(default_config)
            self.local_memory = Memory(config=config)
    
    def export_managed_memories(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export all memories from managed Mem0 service"""
        print("🔄 Exporting memories from managed Mem0 service...")
        
        headers = {
            "Authorization": f"Bearer {self.managed_api_key}",
            "Content-Type": "application/json"
        }
        
        all_memories = []
        page = 1
        
        while True:
            try:
                # Get memories with pagination
                params = {"page": page, "limit": 100}
                if user_id:
                    params["user_id"] = user_id
                
                response = requests.get(
                    f"{self.managed_base_url}/memories",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    memories = data.get("results", [])
                    
                    if not memories:
                        break
                    
                    all_memories.extend(memories)
                    print(f"   Exported page {page}: {len(memories)} memories")
                    page += 1
                    
                elif response.status_code == 404:
                    # No more pages
                    break
                else:
                    print(f"❌ Error exporting memories: {response.status_code} - {response.text}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error during export: {e}")
                break
        
        print(f"✅ Exported {len(all_memories)} memories from managed service")
        return all_memories
    
    def save_export(self, memories: List[Dict[str, Any]], filename: str = None) -> str:
        """Save exported memories to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mem0_export_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_memories": len(memories),
            "memories": memories
        }
        
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"💾 Export saved to: {filename}")
        return filename
    
    def import_to_local(self, memories: List[Dict[str, Any]], verify: bool = True) -> Dict[str, Any]:
        """Import memories to local Mem0 system"""
        print("🔄 Importing memories to local system...")
        
        import_stats = {
            "total_memories": len(memories),
            "successful_imports": 0,
            "failed_imports": 0,
            "errors": []
        }
        
        for i, memory in enumerate(memories):
            try:
                # Extract memory data
                user_id = memory.get("user_id", "migrated_user")
                content = memory.get("memory", "")
                metadata = memory.get("metadata", {})
                
                # Add migration metadata
                enhanced_metadata = {
                    **metadata,
                    "migrated_from": "managed_service",
                    "migration_date": datetime.now().isoformat(),
                    "original_id": memory.get("id"),
                    "original_created_at": memory.get("created_at")
                }
                
                # Format as messages for local system
                messages = [
                    {"role": "user", "content": content},
                    {"role": "assistant", "content": "Memory imported from managed service"}
                ]
                
                # Import to local system
                result = self.local_memory.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=enhanced_metadata
                )
                
                import_stats["successful_imports"] += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   Imported {i + 1}/{len(memories)} memories...")
                
            except Exception as e:
                import_stats["failed_imports"] += 1
                import_stats["errors"].append({
                    "memory_id": memory.get("id"),
                    "error": str(e)
                })
                print(f"❌ Failed to import memory {memory.get('id')}: {e}")
        
        print(f"✅ Import complete: {import_stats['successful_imports']} successful, {import_stats['failed_imports']} failed")
        
        if verify:
            self._verify_import(import_stats)
        
        return import_stats
    
    def _verify_import(self, import_stats: Dict[str, Any]):
        """Verify imported memories"""
        print("🔍 Verifying imported memories...")
        
        try:
            # Get all memories from local system
            all_local_memories = self.local_memory.get_all(user_id="migrated_user")
            migrated_count = len([m for m in all_local_memories 
                                if m.get("metadata", {}).get("migrated_from") == "managed_service"])
            
            print(f"   Found {migrated_count} migrated memories in local system")
            
            if migrated_count == import_stats["successful_imports"]:
                print("✅ Verification successful: All imported memories found")
            else:
                print(f"⚠️  Verification warning: Expected {import_stats['successful_imports']}, found {migrated_count}")
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
    
    def migrate_user(self, user_id: str, backup: bool = True) -> Dict[str, Any]:
        """Complete migration for a specific user"""
        print(f"🚀 Starting migration for user: {user_id}")
        
        # Export memories
        memories = self.export_managed_memories(user_id=user_id)
        
        if not memories:
            print("❌ No memories found to migrate")
            return {"status": "no_data"}
        
        # Save backup if requested
        backup_file = None
        if backup:
            backup_file = self.save_export(memories, f"backup_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Import to local system
        import_stats = self.import_to_local(memories)
        
        migration_summary = {
            "status": "completed",
            "user_id": user_id,
            "backup_file": backup_file,
            "migration_timestamp": datetime.now().isoformat(),
            **import_stats
        }
        
        print("🎉 Migration completed successfully!")
        return migration_summary
    
    def migrate_all_users(self, backup: bool = True) -> Dict[str, Any]:
        """Migrate all memories from managed service"""
        print("🚀 Starting complete migration from managed service...")
        
        # Export all memories
        memories = self.export_managed_memories()
        
        if not memories:
            print("❌ No memories found to migrate")
            return {"status": "no_data"}
        
        # Save backup if requested
        backup_file = None
        if backup:
            backup_file = self.save_export(memories)
        
        # Import to local system
        import_stats = self.import_to_local(memories)
        
        migration_summary = {
            "status": "completed",
            "backup_file": backup_file,
            "migration_timestamp": datetime.now().isoformat(),
            **import_stats
        }
        
        print("🎉 Complete migration finished!")
        return migration_summary

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Migrate memories from managed Mem0 to local system")
    parser.add_argument("--api-key", required=True, help="Managed Mem0 API key")
    parser.add_argument("--user-id", help="Specific user ID to migrate (optional)")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup file")
    parser.add_argument("--export-only", action="store_true", help="Only export, don't import")
    parser.add_argument("--config", help="Path to local config JSON file")
    
    args = parser.parse_args()
    
    # Load local config if provided
    local_config = None
    if args.config:
        with open(args.config, "r") as f:
            local_config = json.load(f)
    
    # Initialize migrator
    migrator = Mem0Migrator(args.api_key, local_config)
    
    if args.export_only:
        # Export only
        memories = migrator.export_managed_memories(args.user_id)
        migrator.save_export(memories)
    else:
        # Full migration
        backup = not args.no_backup
        
        if args.user_id:
            result = migrator.migrate_user(args.user_id, backup=backup)
        else:
            result = migrator.migrate_all_users(backup=backup)
        
        # Save migration summary
        summary_file = f"migration_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"📋 Migration summary saved to: {summary_file}")

if __name__ == "__main__":
    main()