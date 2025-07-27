from mem0 import MemoryClient
import os

# Initialize the client with your API key
client = MemoryClient(api_key="m0-*****5WfV")  # Replace with your actual API key

# Add some memories
def add_memories():
    messages = [
        {"role": "user", "content": "Hi, I'm Gabriel. I'm an innovator and I'm excited about AI memory systems."},
        {"role": "assistant", "content": "Hello Gabriel! I've noted that you're an innovator with a passion for AI memory systems. I'll keep this in mind as we explore technology together."}
    ]
    response = client.add(messages, user_id="gabriel")
    print("Added memories:", response)

# Search for memories
def search_memories():
    query = "What is Gabriel interested in?"
    results = client.search(query, user_id="gabriel")
    print("\nSearch results:")
    for i, result in enumerate(results["results"]):
        print(f"{i+1}. {result['memory']}")

if __name__ == "__main__":
    print("Testing Mem0 API...")
    add_memories()
    search_memories()
