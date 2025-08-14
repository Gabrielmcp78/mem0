#!/usr/bin/env python3
"""
Examples of using the modular FoundationModels package
"""

from apple_intelligence import (
    AppleIntelligenceClient,
    is_apple_intelligence_ready,
    create_semantic_analyzer,
    quick_availability_check
)


def example_simple_usage():
    """Example: Simple usage with high-level client"""
    print("=== Simple Usage Example ===")
    
    # Quick availability check
    if not is_apple_intelligence_ready():
        print("❌ FoundationModels not available")
        return
    
    # Create and use client
    client = AppleIntelligenceClient()
    
    if client.is_ready:
        print("✅ Client ready!")
        
        # Analyze some text
        result = client.analyze_text("Testing FoundationModels integration")
        print(f"Analysis result: {result}")
        
        # Get status
        status = client.get_status()
        print(f"Status: {status}")
    else:
        print("❌ Client initialization failed")


def example_factory_usage():
    """Example: Using factory functions for component creation"""
    print("\n=== Factory Usage Example ===")
    
    # Create analyzer directly
    analyzer = create_semantic_analyzer()
    
    if analyzer:
        print("✅ Semantic analyzer created successfully")
        result = analyzer.analyze("Factory-created analyzer test")
        print(f"Analysis: {result}")
    else:
        print("❌ Failed to create semantic analyzer")


def example_detailed_status():
    """Example: Detailed status checking"""
    print("\n=== Detailed Status Example ===")
    
    status = quick_availability_check()
    print(f"Detailed status: {status}")
    
    if status['available']:
        print("✅ FoundationModels fully available")
    else:
        print(f"❌ Not available: {status['status']}")


def example_backward_compatibility():
    """Example: Using backward compatibility interface"""
    print("\n=== Backward Compatibility Example ===")
    
    # This still works exactly as before
    from apple_intelligence_utils import SimpleAppleIntelligence
    
    ai = SimpleAppleIntelligence()
    if ai.initialize():
        print("✅ Backward compatibility working")
        status = ai.get_status()
        print(f"Status: {status}")
    else:
        print("❌ Initialization failed")


if __name__ == "__main__":
    example_simple_usage()
    example_factory_usage()
    example_detailed_status()
    example_backward_compatibility()