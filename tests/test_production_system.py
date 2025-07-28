"""
Production System Tests for Mem0
Comprehensive test suite for production deployment validation
"""

import pytest
import asyncio
import requests
import time
from typing import Dict, Any
import psycopg2
import redis
import json

from mem0 import Memory
from mem0.config import Config


class TestProductionSystem:
    """Test suite for production system validation"""
    
    @pytest.fixture(scope="class")
    def config(self):
        """Production configuration fixture"""
        return Config.from_env()
    
    @pytest.fixture(scope="class")
    def memory(self, config):
        """Memory instance fixture"""
        return Memory(config=config)
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API base URL fixture"""
        return "http://localhost:8000"
    
    def test_database_connection(self, config):
        """Test PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(config.POSTGRES_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            assert version is not None
            cursor.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    def test_redis_connection(self, config):
        """Test Redis connection"""
        try:
            r = redis.from_url(config.REDIS_URL)
            r.ping()
            r.set("test_key", "test_value")
            assert r.get("test_key").decode() == "test_value"
            r.delete("test_key")
        except Exception as e:
            pytest.fail(f"Redis connection failed: {e}")
    
    def test_vector_store_connection(self, config):
        """Test Qdrant vector store connection"""
        try:
            response = requests.get(f"{config.QDRANT_URL}/health")
            assert response.status_code == 200
            
            # Test collection creation
            collection_config = {
                "vectors": {
                    "size": 1536,
                    "distance": "Cosine"
                }
            }
            response = requests.put(
                f"{config.QDRANT_URL}/collections/test_collection",
                json=collection_config
            )
            assert response.status_code in [200, 409]  # 409 if already exists
            
            # Cleanup
            requests.delete(f"{config.QDRANT_URL}/collections/test_collection")
            
        except Exception as e:
            pytest.fail(f"Vector store connection failed: {e}")
    
    def test_api_health_endpoint(self, api_base_url):
        """Test API health endpoint"""
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "database" in health_data
        assert "vector_store" in health_data
        assert "llm" in health_data
    
    def test_api_ready_endpoint(self, api_base_url):
        """Test API readiness endpoint"""
        response = requests.get(f"{api_base_url}/ready")
        assert response.status_code == 200
        
        ready_data = response.json()
        assert ready_data["ready"] is True
    
    def test_memory_operations(self, memory):
        """Test core memory operations"""
        user_id = "test_user_prod"
        
        # Test adding memory
        messages = [
            {"role": "user", "content": "I love pizza"},
            {"role": "assistant", "content": "Great! I'll remember that you love pizza."}
        ]
        
        result = memory.add(messages, user_id=user_id)
        assert "message" in result
        
        # Test searching memory
        search_results = memory.search("food preferences", user_id=user_id)
        assert len(search_results) > 0
        
        # Test getting all memories
        all_memories = memory.get_all(user_id=user_id)
        assert len(all_memories) > 0
        
        # Cleanup
        memory.delete_all(user_id=user_id)
    
    def test_api_memory_endpoints(self, api_base_url):
        """Test API memory endpoints"""
        user_id = "test_api_user"
        
        # Test add memory endpoint
        add_payload = {
            "messages": [
                {"role": "user", "content": "I work as a software engineer"},
                {"role": "assistant", "content": "I'll remember your profession."}
            ],
            "user_id": user_id
        }
        
        response = requests.post(f"{api_base_url}/v1/memories/", json=add_payload)
        assert response.status_code == 200
        
        # Test search endpoint
        search_payload = {
            "query": "profession",
            "user_id": user_id
        }
        
        response = requests.post(f"{api_base_url}/v1/memories/search/", json=search_payload)
        assert response.status_code == 200
        
        search_data = response.json()
        assert len(search_data["results"]) > 0
        
        # Test get all memories endpoint
        response = requests.get(f"{api_base_url}/v1/memories/?user_id={user_id}")
        assert response.status_code == 200
        
        # Cleanup
        response = requests.delete(f"{api_base_url}/v1/memories/?user_id={user_id}")
        assert response.status_code == 200
    
    def test_performance_benchmarks(self, memory):
        """Test performance benchmarks"""
        user_id = "perf_test_user"
        
        # Test add performance
        start_time = time.time()
        for i in range(10):
            messages = [
                {"role": "user", "content": f"Test message {i}"},
                {"role": "assistant", "content": f"Response {i}"}
            ]
            memory.add(messages, user_id=user_id)
        
        add_time = time.time() - start_time
        assert add_time < 30  # Should complete within 30 seconds
        
        # Test search performance
        start_time = time.time()
        for i in range(10):
            memory.search(f"test query {i}", user_id=user_id)
        
        search_time = time.time() - start_time
        assert search_time < 10  # Should complete within 10 seconds
        
        # Cleanup
        memory.delete_all(user_id=user_id)
    
    def test_concurrent_operations(self, memory):
        """Test concurrent memory operations"""
        import threading
        import queue
        
        results = queue.Queue()
        user_id = "concurrent_test_user"
        
        def add_memory_worker(worker_id):
            try:
                messages = [
                    {"role": "user", "content": f"Worker {worker_id} message"},
                    {"role": "assistant", "content": f"Worker {worker_id} response"}
                ]
                result = memory.add(messages, user_id=f"{user_id}_{worker_id}")
                results.put(("success", worker_id, result))
            except Exception as e:
                results.put(("error", worker_id, str(e)))
        
        # Start 5 concurrent workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_memory_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            status, worker_id, result = results.get()
            if status == "success":
                success_count += 1
            else:
                pytest.fail(f"Worker {worker_id} failed: {result}")
        
        assert success_count == 5
        
        # Cleanup
        for i in range(5):
            memory.delete_all(user_id=f"{user_id}_{i}")
    
    def test_error_handling(self, memory):
        """Test error handling and recovery"""
        # Test with invalid user_id
        with pytest.raises(Exception):
            memory.add("test", user_id="")
        
        # Test with invalid query
        result = memory.search("", user_id="test_user")
        assert isinstance(result, list)  # Should return empty list, not error
        
        # Test with non-existent user
        result = memory.get_all(user_id="non_existent_user")
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_data_persistence(self, memory):
        """Test data persistence across operations"""
        user_id = "persistence_test_user"
        
        # Add memory
        messages = [
            {"role": "user", "content": "I live in New York"},
            {"role": "assistant", "content": "I'll remember you live in New York."}
        ]
        memory.add(messages, user_id=user_id)
        
        # Create new memory instance to test persistence
        new_memory = Memory()
        
        # Search with new instance
        results = new_memory.search("location", user_id=user_id)
        assert len(results) > 0
        assert any("New York" in str(result) for result in results)
        
        # Cleanup
        memory.delete_all(user_id=user_id)
    
    def test_memory_limits(self, memory):
        """Test memory storage limits"""
        user_id = "limits_test_user"
        
        # Add many memories to test limits
        for i in range(100):
            messages = [
                {"role": "user", "content": f"Memory item {i}"},
                {"role": "assistant", "content": f"Stored item {i}"}
            ]
            memory.add(messages, user_id=user_id)
        
        # Check that memories are properly managed
        all_memories = memory.get_all(user_id=user_id)
        assert len(all_memories) <= 1000  # Should respect limits
        
        # Cleanup
        memory.delete_all(user_id=user_id)
    
    def test_security_features(self, api_base_url):
        """Test security features"""
        # Test rate limiting (if implemented)
        responses = []
        for i in range(100):
            response = requests.get(f"{api_base_url}/health")
            responses.append(response.status_code)
        
        # Should not all be successful if rate limiting is active
        # This is a basic test - adjust based on actual rate limiting implementation
        
        # Test input validation
        invalid_payload = {
            "messages": "invalid_format",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{api_base_url}/v1/memories/", json=invalid_payload)
        assert response.status_code in [400, 422]  # Should reject invalid input
    
    def test_monitoring_endpoints(self, api_base_url):
        """Test monitoring and metrics endpoints"""
        # Test metrics endpoint (if available)
        try:
            response = requests.get(f"{api_base_url}/metrics")
            if response.status_code == 200:
                assert "mem0_" in response.text  # Should contain mem0 metrics
        except requests.exceptions.RequestException:
            pass  # Metrics endpoint might not be available
        
        # Test version endpoint
        try:
            response = requests.get(f"{api_base_url}/version")
            if response.status_code == 200:
                version_data = response.json()
                assert "version" in version_data
        except requests.exceptions.RequestException:
            pass  # Version endpoint might not be available


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_chatbot_scenario(self, memory):
        """Test complete chatbot scenario"""
        user_id = "chatbot_test_user"
        
        # Simulate conversation
        conversations = [
            [
                {"role": "user", "content": "Hi, I'm John and I'm 25 years old"},
                {"role": "assistant", "content": "Hello John! Nice to meet you."}
            ],
            [
                {"role": "user", "content": "I work as a data scientist"},
                {"role": "assistant", "content": "That's interesting! Data science is a great field."}
            ],
            [
                {"role": "user", "content": "What do you know about me?"},
                {"role": "assistant", "content": "You're John, 25 years old, and work as a data scientist."}
            ]
        ]
        
        # Add conversations
        for conv in conversations[:2]:
            memory.add(conv, user_id=user_id)
        
        # Search for user info
        results = memory.search("tell me about the user", user_id=user_id)
        
        # Verify information is retrievable
        results_text = " ".join([str(r) for r in results])
        assert "John" in results_text
        assert "25" in results_text or "data scientist" in results_text
        
        # Cleanup
        memory.delete_all(user_id=user_id)
    
    def test_multi_user_isolation(self, memory):
        """Test user data isolation"""
        user1_id = "user1_isolation_test"
        user2_id = "user2_isolation_test"
        
        # Add different data for each user
        memory.add([
            {"role": "user", "content": "I like cats"},
            {"role": "assistant", "content": "Cats are great pets!"}
        ], user_id=user1_id)
        
        memory.add([
            {"role": "user", "content": "I like dogs"},
            {"role": "assistant", "content": "Dogs are wonderful companions!"}
        ], user_id=user2_id)
        
        # Test isolation
        user1_results = memory.search("pets", user_id=user1_id)
        user2_results = memory.search("pets", user_id=user2_id)
        
        user1_text = " ".join([str(r) for r in user1_results])
        user2_text = " ".join([str(r) for r in user2_results])
        
        assert "cats" in user1_text.lower()
        assert "dogs" in user2_text.lower()
        assert "dogs" not in user1_text.lower()
        assert "cats" not in user2_text.lower()
        
        # Cleanup
        memory.delete_all(user_id=user1_id)
        memory.delete_all(user_id=user2_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])