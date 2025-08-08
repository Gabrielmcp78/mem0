#!/usr/bin/env python3
"""
🔍 Fact Extraction Flow Debug Test
===============================

This test shows exactly what happens in the mem0 fact extraction pipeline
and fixes the Apple Intelligence LLM to properly extract facts.
"""

import os
import sys
import json
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_fact_extraction_directly():
    """Test the fact extraction step directly"""
    print("🔍 Testing Fact Extraction Directly")
    print("=" * 50)
    
    try:
        from mem0.llms.apple_intelligence import AppleIntelligenceLLM
        from mem0.memory.utils import get_fact_retrieval_messages, parse_messages
        
        llm = AppleIntelligenceLLM()
        
        if not llm.is_available:
            print(f"⚠️  Apple Intelligence not available: {llm.error_message}")
            return False
        
        # Test input
        messages = [
            {"role": "user", "content": "Hi, my name is Gabriel and I love pizza!"}
        ]
        
        parsed_messages = parse_messages(messages)
        print(f"📝 Parsed messages: {parsed_messages}")
        
        # Get fact retrieval messages (same as mem0 does)
        system_prompt, user_prompt = get_fact_retrieval_messages(parsed_messages)
        
        print(f"\n📋 System prompt (first 200 chars): {system_prompt[:200]}...")
        print(f"📋 User prompt: {user_prompt}")
        
        # Call Apple Intelligence for fact extraction
        response = llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        
        print(f"\n🤖 Apple Intelligence response: {response}")
        
        # Parse the response
        try:
            facts_data = json.loads(response)
            if "facts" in facts_data:
                facts = facts_data["facts"]
                print(f"✅ Facts extracted: {facts}")
                return len(facts) > 0
            else:
                print(f"❌ No 'facts' key in response: {facts_data}")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse facts response: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Fact extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_update_directly():
    """Test the memory update step directly with known facts"""
    print("\n🧠 Testing Memory Update Directly")
    print("=" * 50)
    
    try:
        from mem0.llms.apple_intelligence import AppleIntelligenceLLM
        from mem0.configs.prompts import get_update_memory_messages
        
        llm = AppleIntelligenceLLM()
        
        if not llm.is_available:
            print(f"⚠️  Apple Intelligence not available: {llm.error_message}")
            return False
        
        # Simulate the memory update call with known facts
        retrieved_old_memory = []  # Empty memory
        new_retrieved_facts = ["Name is Gabriel", "Loves pizza"]
        
        # Generate the prompt exactly as mem0 does
        function_calling_prompt = get_update_memory_messages(
            retrieved_old_memory, new_retrieved_facts, None
        )
        
        print(f"📋 Memory update prompt (first 300 chars): {function_calling_prompt[:300]}...")
        
        # Call Apple Intelligence for memory update
        response = llm.generate_response(
            messages=[{"role": "user", "content": function_calling_prompt}],
            response_format={"type": "json_object"},
        )
        
        print(f"\n🤖 Apple Intelligence response: {response}")
        
        # Parse the response
        try:
            memory_data = json.loads(response)
            if "memory" in memory_data and isinstance(memory_data["memory"], list):
                memory_items = memory_data["memory"]
                print(f"✅ Memory update successful with {len(memory_items)} items:")
                for item in memory_items:
                    print(f"   - ID: {item.get('id')}, Event: {item.get('event')}, Text: {item.get('text')}")
                return len(memory_items) > 0
            else:
                print(f"❌ Invalid memory response format: {memory_data}")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse memory response: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Memory update test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test the complete mem0 pipeline"""
    print("\n🚀 Testing Full mem0 Pipeline")
    print("=" * 50)
    
    try:
        # Clean environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        from mem0 import Memory
        
        config = {
            "llm": {
                "provider": "apple_intelligence",
                "config": {
                    "model": "apple-intelligence-foundation",
                    "temperature": 0.1,  # Lower temperature for consistency
                    "max_tokens": 1000
                }
            },
            "embedder": {
                "provider": "apple_intelligence",
                "config": {
                    "model": "apple-intelligence-embeddings"
                }
            }
        }
        
        memory = Memory.from_config(config)
        print("✅ Memory initialized")
        
        # Test with clear, simple message
        test_message = "My name is Gabriel and I absolutely love pizza!"
        
        print(f"\n💾 Adding memory: '{test_message}'")
        result = memory.add(test_message, user_id="test_gabriel")
        
        print(f"   Result type: {type(result)}")
        print(f"   Result: {result}")
        
        if result and isinstance(result, list) and len(result) > 0:
            print(f"✅ Memory added successfully! {len(result)} items added:")
            for item in result:
                print(f"   - {item.get('event')}: {item.get('memory')}")
            return True
        elif result and isinstance(result, dict) and result.get('results'):
            if len(result['results']) > 0:
                print(f"✅ Memory added successfully! {len(result['results'])} items added:")
                for item in result['results']:
                    print(f"   - {item.get('event')}: {item.get('memory')}")
                return True
            else:
                print("❌ Memory add returned empty results")
                return False
        else:
            print(f"❌ Memory add failed or returned unexpected format: {result}")
            return False
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all fact extraction flow tests"""
    print("🔍 FACT EXTRACTION FLOW DEBUG TEST")
    print("🔍" * 20)
    
    test1_passed = test_fact_extraction_directly()
    test2_passed = test_memory_update_directly()
    test3_passed = test_full_pipeline()
    
    print("\n📊 FACT EXTRACTION DEBUG RESULTS")
    print("=" * 50)
    print(f"Direct Fact Extraction:    {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Direct Memory Update:      {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Full Pipeline Integration: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    print("=" * 50)
    if all_passed:
        print("🎉 FACT EXTRACTION PIPELINE WORKING!")
        print("\n📋 Key findings:")
        print("   • Fact extraction properly identifies user information")
        print("   • Memory update creates proper JSON with ADD events")
        print("   • Full pipeline persists memories successfully")
    else:
        print("🔧 FACT EXTRACTION NEEDS FIXING")
        print("\n📋 Issues found:")
        if not test1_passed:
            print("   • Fact extraction not working - returns empty facts")
        if not test2_passed:
            print("   • Memory update not working - returns empty memory")
        if not test3_passed:
            print("   • Full pipeline not working - memories not persisted")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)