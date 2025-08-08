#!/usr/bin/env python3
"""
🎯 Direct Memory Operations Test
============================

This test directly calls memory operations to see exactly what's happening
with the JSON response handling.
"""

import os
import sys
import json
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)

def test_direct_apple_intelligence_call():
    """Test direct Apple Intelligence LLM call with memory prompt"""
    print("🧪 Direct Apple Intelligence LLM Test")
    print("=" * 50)
    
    try:
        from mem0.llms.apple_intelligence import AppleIntelligenceLLM
        
        llm = AppleIntelligenceLLM()
        
        if not llm.is_available:
            print(f"⚠️  Apple Intelligence not available: {llm.error_message}")
            return False
        
        # Test memory update with specific mem0 format
        print("\n🧠 Testing memory update with exact mem0 format:")
        
        memory_prompt = """You are a smart memory manager which controls the memory of a system.
You can perform four operations: (1) add into the memory, (2) update the memory, (3) delete from the memory, and (4) no change.

Based on the above four operations, the memory will change.

Compare newly retrieved facts with the existing memory. For each new fact, decide whether to:
- ADD: Add it to the memory as a new element
- UPDATE: Update an existing memory element
- DELETE: Delete an existing memory element
- NONE: Make no change (if the fact is already present or irrelevant)

Below is the current content of my memory which I have collected till now. You have to update it in the following format only:

```
[]
```

The new retrieved facts are mentioned in the triple backticks. You have to analyze the new retrieved facts and determine whether these facts should be added, updated, or deleted in the memory.

```
["Gabriel loves pizza and uses Apple Intelligence for memory operations"]
```

You must return your response in the following JSON structure only:

{
    "memory" : [
        {
            "id" : "<ID of the memory>",                # Use existing ID for updates/deletes, or new ID for additions
            "text" : "<Content of the memory>",         # Content of the memory
            "event" : "<Operation to be performed>",    # Must be "ADD", "UPDATE", "DELETE", or "NONE"
            "old_memory" : "<Old memory content>"       # Required only if the event is "UPDATE"
        },
        ...
    ]
}

Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- If the current memory is empty, then you have to add the new retrieved facts to the memory.
- You should return the updated memory in only JSON format as shown below. The memory key should be the same if no changes are made.
- If there is an addition, generate a new key and add the new memory corresponding to it.
- If there is a deletion, the memory key-value pair should be removed from the memory.
- If there is an update, the ID key should remain the same and only the value needs to be updated.

Do not return anything except the JSON format."""
        
        messages = [{"role": "user", "content": memory_prompt}]
        
        # Call Apple Intelligence directly
        response = llm.generate_response(
            messages,
            response_format={"type": "json_object"}
        )
        
        print(f"Raw response: '{response}'")
        print(f"Response type: {type(response)}")
        
        # Try to parse response
        try:
            if isinstance(response, str):
                parsed = json.loads(response)
                print(f"✅ Parsed JSON successfully: {parsed}")
                
                if "memory" in parsed and isinstance(parsed["memory"], list):
                    print(f"✅ Memory structure correct with {len(parsed['memory'])} items")
                    for item in parsed["memory"]:
                        print(f"   - ID: {item.get('id')}, Event: {item.get('event')}, Text: {item.get('text')}")
                else:
                    print(f"❌ Memory structure incorrect: {parsed}")
            else:
                print(f"❌ Response is not a string: {response}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"   Raw response: '{response}'")
            
        return True
        
    except Exception as e:
        print(f"❌ Direct Apple Intelligence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_memory_creation():
    """Test manual memory creation to isolate the issue"""
    print("\n🔧 Manual Memory Creation Test")
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
                    "temperature": 0.1,  # Lower temperature for more consistent output
                    "max_tokens": 500
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
        
        # Test very simple add operation
        print("\n💾 Testing simple add:")
        simple_message = "Gabriel likes pizza"
        
        try:
            result = memory.add(simple_message, user_id="test_user")
            print(f"   Add result type: {type(result)}")
            print(f"   Add result: {result}")
            
            if result and isinstance(result, dict) and 'results' in result:
                print(f"   ✅ Add successful with {len(result['results'])} results")
            else:
                print(f"   ❌ Add returned unexpected format: {result}")
                
        except Exception as add_error:
            print(f"   ❌ Add failed: {add_error}")
            import traceback
            traceback.print_exc()
        
        # Test search with proper error handling
        print("\n🔍 Testing search with error handling:")
        try:
            search_results = memory.search("Gabriel pizza", user_id="test_user", limit=5)
            print(f"   Search results type: {type(search_results)}")
            print(f"   Search results: {search_results}")
            
            if isinstance(search_results, list):
                print(f"   ✅ Search returned list with {len(search_results)} items")
                for i, result in enumerate(search_results):
                    print(f"      [{i}] Type: {type(result)}, Content: {result}")
            else:
                print(f"   ❌ Search didn't return list: {search_results}")
                
        except Exception as search_error:
            print(f"   ❌ Search failed: {search_error}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Manual memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run focused tests"""
    print("🎯 DIRECT MEMORY OPERATIONS DEBUG TEST")
    print("🎯" * 20)
    
    test1_passed = test_direct_apple_intelligence_call()
    test2_passed = test_manual_memory_creation()
    
    print("\n📊 DEBUG TEST RESULTS")
    print("=" * 50)
    print(f"Direct Apple Intelligence Call: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Manual Memory Creation:         {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)