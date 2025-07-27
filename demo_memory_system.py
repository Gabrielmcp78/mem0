#!/usr/bin/env python3
"""
Demo of the Local Memory Ecosystem
Shows off key capabilities with different agent scenarios
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
import time

def create_memory_config():
    """Create the standard Ollama configuration"""
    return MemoryConfig(
        llm=LlmConfig(
            provider="ollama",
            config={
                "model": "llama3.2:3b",
                "ollama_base_url": "http://localhost:11434"
            }
        ),
        embedder=EmbedderConfig(
            provider="ollama", 
            config={
                "model": "nomic-embed-text",
                "ollama_base_url": "http://localhost:11434",
                "embedding_dims": 768
            }
        ),
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "host": "localhost",
                "port": 6333,
                "collection_name": "demo_memories",
                "embedding_model_dims": 768
            }
        )
    )

def demo_personal_assistant():
    """Demo: Personal Assistant with Memory"""
    print("\n" + "="*60)
    print("🤖 DEMO: Personal Assistant with Memory")
    print("="*60)
    
    memory = Memory(create_memory_config())
    user_id = "alice"
    
    # Simulate conversation history
    memories = [
        "I work as a software engineer at TechCorp",
        "My favorite programming language is Python",
        "I'm working on a machine learning project about image recognition",
        "I have a meeting with the product team every Tuesday at 2 PM",
        "I prefer to work in the morning, I'm most productive before 11 AM",
        "I'm learning about transformers and attention mechanisms"
    ]
    
    print("📝 Building personal memory profile...")
    for memory_text in memories:
        result = memory.add(memory_text, user_id=user_id)
        print(f"  + {memory_text}")
        time.sleep(0.5)  # Simulate real conversation timing
    
    # Query the memories
    queries = [
        "What do I do for work?",
        "What programming languages do I like?",
        "What am I learning about?",
        "When are my meetings?"
    ]
    
    print(f"\n🔍 Querying {user_id}'s memories:")
    for query in queries:
        results = memory.search(query, user_id=user_id)
        print(f"\nQ: {query}")
        for i, result in enumerate(results['results'][:2]):  # Top 2 results
            print(f"  {i+1}. {result['memory']} (score: {result['score']:.3f})")

def demo_multi_user_system():
    """Demo: Multi-User System with Isolated Memories"""
    print("\n" + "="*60)
    print("👥 DEMO: Multi-User System with Memory Isolation")
    print("="*60)
    
    memory = Memory(create_memory_config())
    
    # Different users with different preferences
    users = {
        "developer": [
            "I love coding in JavaScript and React",
            "I'm building a web application for e-commerce",
            "I prefer VS Code as my editor"
        ],
        "designer": [
            "I specialize in UI/UX design",
            "I use Figma for all my design work",
            "I'm passionate about accessibility and inclusive design"
        ],
        "manager": [
            "I oversee the product development team",
            "We use Agile methodology with 2-week sprints",
            "I focus on stakeholder communication and roadmap planning"
        ]
    }
    
    # Add memories for each user
    print("📝 Adding memories for different users...")
    for user_id, user_memories in users.items():
        print(f"\n{user_id.upper()}:")
        for memory_text in user_memories:
            memory.add(memory_text, user_id=user_id)
            print(f"  + {memory_text}")
    
    # Test memory isolation
    print(f"\n🔍 Testing memory isolation:")
    query = "What tools do you use?"
    
    for user_id in users.keys():
        results = memory.search(query, user_id=user_id)
        print(f"\n{user_id.upper()} memories for '{query}':")
        for i, result in enumerate(results['results'][:2]):
            print(f"  {i+1}. {result['memory']} (score: {result['score']:.3f})")

def demo_agent_collaboration():
    """Demo: Agent Collaboration with Shared Context"""
    print("\n" + "="*60)
    print("🤝 DEMO: Agent Collaboration with Shared Context")
    print("="*60)
    
    memory = Memory(create_memory_config())
    
    # Simulate a collaborative project
    project_context = [
        "We're building a customer support chatbot",
        "The chatbot should handle common questions about billing",
        "We need to integrate with the existing CRM system",
        "The target response time is under 2 seconds",
        "We're using Python with FastAPI for the backend"
    ]
    
    agent_contributions = {
        "architect": [
            "I recommend using a microservices architecture",
            "We should implement caching for frequently asked questions",
            "The system should be horizontally scalable"
        ],
        "developer": [
            "I'll implement the FastAPI endpoints",
            "We can use Redis for caching the responses",
            "I suggest using async/await for better performance"
        ],
        "tester": [
            "We need comprehensive unit tests for all endpoints",
            "I'll set up automated testing for response times",
            "We should test with various customer scenarios"
        ]
    }
    
    # Add shared project context
    print("📋 Adding shared project context...")
    for context in project_context:
        memory.add(context, user_id="project_shared")
        print(f"  + {context}")
    
    # Add agent-specific contributions
    print(f"\n👥 Adding agent contributions...")
    for agent_id, contributions in agent_contributions.items():
        print(f"\n{agent_id.upper()}:")
        for contribution in contributions:
            memory.add(contribution, user_id=agent_id)
            print(f"  + {contribution}")
    
    # Query for collaboration
    collaboration_queries = [
        "What architecture should we use?",
        "How can we improve performance?",
        "What testing is needed?"
    ]
    
    print(f"\n🔍 Collaborative knowledge queries:")
    for query in collaboration_queries:
        print(f"\nQ: {query}")
        
        # Search across all agents and shared context
        all_results = []
        for search_user in ["project_shared"] + list(agent_contributions.keys()):
            results = memory.search(query, user_id=search_user)
            for result in results['results']:
                result['source'] = search_user
                all_results.append(result)
        
        # Sort by relevance and show top results
        all_results.sort(key=lambda x: x['score'], reverse=True)
        for i, result in enumerate(all_results[:3]):
            print(f"  {i+1}. [{result['source']}] {result['memory']} (score: {result['score']:.3f})")

def demo_learning_system():
    """Demo: Learning System that Builds Knowledge Over Time"""
    print("\n" + "="*60)
    print("🧠 DEMO: Learning System Building Knowledge Over Time")
    print("="*60)
    
    memory = Memory(create_memory_config())
    user_id = "learning_agent"
    
    # Simulate learning progression
    learning_stages = [
        {
            "stage": "Basics",
            "memories": [
                "Machine learning is a subset of artificial intelligence",
                "Supervised learning uses labeled training data",
                "Unsupervised learning finds patterns in unlabeled data"
            ]
        },
        {
            "stage": "Intermediate",
            "memories": [
                "Neural networks are inspired by biological neurons",
                "Backpropagation is used to train neural networks",
                "Overfitting occurs when a model memorizes training data"
            ]
        },
        {
            "stage": "Advanced",
            "memories": [
                "Transformers use attention mechanisms for sequence processing",
                "BERT is a bidirectional transformer for language understanding",
                "GPT models are autoregressive transformers for text generation"
            ]
        }
    ]
    
    # Add learning progression
    print("📚 Simulating learning progression...")
    for stage_info in learning_stages:
        print(f"\n{stage_info['stage'].upper()} STAGE:")
        for memory_text in stage_info['memories']:
            memory.add(memory_text, user_id=user_id)
            print(f"  + {memory_text}")
        time.sleep(1)
    
    # Test knowledge retrieval
    knowledge_queries = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are transformers?",
        "Tell me about BERT and GPT"
    ]
    
    print(f"\n🎓 Testing accumulated knowledge:")
    for query in knowledge_queries:
        results = memory.search(query, user_id=user_id)
        print(f"\nQ: {query}")
        for i, result in enumerate(results['results'][:2]):
            print(f"  {i+1}. {result['memory']} (score: {result['score']:.3f})")

def main():
    """Run all demos"""
    print("🌟 LOCAL MEMORY ECOSYSTEM DEMO")
    print("Showcasing capabilities with Ollama + Qdrant + Mem0")
    
    try:
        demo_personal_assistant()
        demo_multi_user_system()
        demo_agent_collaboration()
        demo_learning_system()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETE!")
        print("="*60)
        print("✅ Personal assistant memory")
        print("✅ Multi-user memory isolation") 
        print("✅ Agent collaboration with shared context")
        print("✅ Learning system with knowledge accumulation")
        print("\n🚀 Your local memory ecosystem is ready for any agent framework!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure Ollama is running with the required models:")
        print("  ollama pull llama3.2:3b")
        print("  ollama pull nomic-embed-text")
        print("And that Qdrant is running on port 16333")

if __name__ == "__main__":
    main()