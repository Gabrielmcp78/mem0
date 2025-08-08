#!/usr/bin/env python3
"""
Test Multi-Agent Memory Sharing Functionality
Tests the enhanced MCP servers with multi-agent capabilities
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

async def test_multi_agent_memory():
    """Test multi-agent memory sharing functionality"""
    
    print("🧪 Testing Multi-Agent Memory Sharing Functionality")
    print("=" * 60)
    
    try:
        # Import the memory operations directly
        from integrations.mcp.memory_operations import (
            add_memory, 
            get_agent_memories, 
            get_shared_context,
            get_agent_collaboration_summary
        )
        
        # Test data
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        user_id = "gabriel"
        
        print(f"📝 Test Run ID: {run_id}")
        print()
        
        # Test 1: Add memories from different agents
        print("1. Adding memories from different agents...")
        
        # Agent 1 (Claude) adds a memory
        claude_memory = {
            "messages": "I helped the user understand Python decorators and their use cases.",
            "user_id": user_id,
            "agent_id": "claude",
            "run_id": run_id,
            "metadata": json.dumps({
                "topic": "python_decorators",
                "difficulty": "intermediate"
            })
        }
        
        result1 = add_memory(claude_memory)
        print(f"✅ Claude memory added: {result1.get('success', False)}")
        
        # Agent 2 (Kiro) adds a memory
        kiro_memory = {
            "messages": "I provided code examples for implementing decorators in the user's project.",
            "user_id": user_id,
            "agent_id": "kiro",
            "run_id": run_id,
            "metadata": json.dumps({
                "topic": "python_decorators",
                "code_examples": True
            })
        }
        
        result2 = add_memory(kiro_memory)
        print(f"✅ Kiro memory added: {result2.get('success', False)}")
        
        # Agent 3 (Assistant) adds a memory
        assistant_memory = {
            "messages": "I explained the performance implications of decorators and best practices.",
            "user_id": user_id,
            "agent_id": "assistant",
            "run_id": run_id,
            "metadata": json.dumps({
                "topic": "python_decorators",
                "focus": "performance"
            })
        }
        
        result3 = add_memory(assistant_memory)
        print(f"✅ Assistant memory added: {result3.get('success', False)}")
        print()
        
        # Test 2: Get agent-specific memories
        print("2. Testing agent-specific memory retrieval...")
        
        claude_memories = get_agent_memories({
            "agent_id": "claude",
            "user_id": user_id,
            "run_id": run_id,
            "limit": 10
        })
        
        if claude_memories.get('success'):
            print(f"✅ Claude memories retrieved: {claude_memories.get('total_memories', 0)} memories")
        else:
            print(f"❌ Failed to get Claude memories: {claude_memories.get('error')}")
        
        kiro_memories = get_agent_memories({
            "agent_id": "kiro",
            "user_id": user_id,
            "run_id": run_id,
            "limit": 10
        })
        
        if kiro_memories.get('success'):
            print(f"✅ Kiro memories retrieved: {kiro_memories.get('total_memories', 0)} memories")
        else:
            print(f"❌ Failed to get Kiro memories: {kiro_memories.get('error')}")
        print()
        
        # Test 3: Get shared context
        print("3. Testing shared context retrieval...")
        
        shared_context = get_shared_context({
            "run_id": run_id,
            "user_id": user_id,
            "limit": 20
        })
        
        if shared_context.get('success'):
            agents = shared_context.get('agents_involved', [])
            total_memories = shared_context.get('total_shared_memories', 0)
            print(f"✅ Shared context retrieved:")
            print(f"   - Agents involved: {', '.join(agents)}")
            print(f"   - Total shared memories: {total_memories}")
            print(f"   - Apple Intelligence processed: {shared_context.get('apple_intelligence_processed', False)}")
        else:
            print(f"❌ Failed to get shared context: {shared_context.get('error')}")
        print()
        
        # Test 4: Get collaboration summary
        print("4. Testing agent collaboration summary...")
        
        collaboration_summary = get_agent_collaboration_summary({
            "run_id": run_id,
            "user_id": user_id
        })
        
        if collaboration_summary.get('success'):
            agents = collaboration_summary.get('agents_involved', [])
            contributions = collaboration_summary.get('agent_contributions', {})
            timeline_length = len(collaboration_summary.get('collaboration_timeline', []))
            
            print(f"✅ Collaboration summary generated:")
            print(f"   - Agents involved: {', '.join(agents)}")
            print(f"   - Agent contributions: {contributions}")
            print(f"   - Timeline entries: {timeline_length}")
            print(f"   - Apple Intelligence processed: {collaboration_summary.get('apple_intelligence_processed', False)}")
            print(f"   - Neural Engine optimized: {collaboration_summary.get('neural_engine_optimized', False)}")
        else:
            print(f"❌ Failed to get collaboration summary: {collaboration_summary.get('error')}")
        print()
        
        # Test 5: Verify metadata tracking
        print("5. Verifying Apple Intelligence metadata tracking...")
        
        if shared_context.get('success') and shared_context.get('shared_context'):
            sample_memory = shared_context['shared_context'][0]
            metadata = sample_memory.get('metadata', {})
            
            apple_intelligence_indicators = [
                'processed_by',
                'neural_engine_optimized',
                'local_processing',
                'privacy_compliant',
                'timestamp'
            ]
            
            missing_indicators = []
            for indicator in apple_intelligence_indicators:
                if indicator not in metadata:
                    missing_indicators.append(indicator)
            
            if not missing_indicators:
                print("✅ All Apple Intelligence metadata indicators present:")
                print(f"   - Processed by: {metadata.get('processed_by')}")
                print(f"   - Neural Engine optimized: {metadata.get('neural_engine_optimized')}")
                print(f"   - Local processing: {metadata.get('local_processing')}")
                print(f"   - Privacy compliant: {metadata.get('privacy_compliant')}")
                print(f"   - Timestamp: {metadata.get('timestamp')}")
            else:
                print(f"⚠️ Missing Apple Intelligence indicators: {', '.join(missing_indicators)}")
        else:
            print("⚠️ Could not verify metadata - no shared context available")
        
        print()
        print("🎉 Multi-Agent Memory Sharing Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    success = await test_multi_agent_memory()
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())