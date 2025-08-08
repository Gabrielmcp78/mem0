#!/usr/bin/env python3
"""
Agent Registration System for Multi-Agent Memory
Handles agent registration, session management, and memory coordination
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

class AgentRegistry:
    """Manages agent registration and session tracking"""
    
    def __init__(self):
        self.registry_file = "/tmp/agent_registry.json"
        self.active_sessions = {}
        self.load_registry()
    
    def load_registry(self):
        """Load existing agent registry"""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.active_sessions = data.get('active_sessions', {})
            else:
                self.active_sessions = {}
        except Exception as e:
            print(f"Error loading registry: {e}")
            self.active_sessions = {}
    
    def save_registry(self):
        """Save agent registry to file"""
        try:
            data = {
                'active_sessions': self.active_sessions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def register_agent(self, agent_id: str, user_id: str = "gabriel", 
                      session_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Register an agent for memory operations"""
        
        if not agent_id:
            return {"error": "agent_id is required"}
        
        # Generate session ID
        session_id = f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create agent session
        agent_session = {
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "memory_count": 0,
            "last_activity": datetime.now().isoformat()
        }
        
        # Add optional session info
        if session_info:
            agent_session.update(session_info)
        
        # Store in active sessions
        self.active_sessions[session_id] = agent_session
        self.save_registry()
        
        return {
            "success": True,
            "session_id": session_id,
            "agent_id": agent_id,
            "message": f"Agent {agent_id} registered successfully",
            "registration_time": agent_session["registered_at"]
        }
    
    def get_agent_session(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent session for an agent"""
        
        # Find the most recent session for this agent
        agent_sessions = [
            session for session in self.active_sessions.values()
            if session.get("agent_id") == agent_id and session.get("status") == "active"
        ]
        
        if agent_sessions:
            # Return the most recent session
            return max(agent_sessions, key=lambda x: x.get("registered_at", ""))
        
        return None
    
    def update_agent_activity(self, agent_id: str, activity_type: str = "memory_operation"):
        """Update agent's last activity"""
        
        session = self.get_agent_session(agent_id)
        if session:
            session_id = session["session_id"]
            self.active_sessions[session_id]["last_activity"] = datetime.now().isoformat()
            
            if activity_type == "memory_operation":
                self.active_sessions[session_id]["memory_count"] += 1
            
            self.save_registry()
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all currently active agents"""
        
        active_agents = []
        for session in self.active_sessions.values():
            if session.get("status") == "active":
                active_agents.append(session)
        
        return active_agents
    
    def deregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deregister an agent"""
        
        session = self.get_agent_session(agent_id)
        if session:
            session_id = session["session_id"]
            self.active_sessions[session_id]["status"] = "inactive"
            self.active_sessions[session_id]["deregistered_at"] = datetime.now().isoformat()
            self.save_registry()
            
            return {
                "success": True,
                "message": f"Agent {agent_id} deregistered successfully"
            }
        
        return {"error": f"Agent {agent_id} not found in registry"}

# Global registry instance
_agent_registry = AgentRegistry()

def register_agent(agent_id: str, user_id: str = "gabriel", **kwargs) -> Dict[str, Any]:
    """Register an agent with the memory system"""
    return _agent_registry.register_agent(agent_id, user_id, kwargs)

def get_my_session(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get current session for an agent"""
    return _agent_registry.get_agent_session(agent_id)

def update_my_activity(agent_id: str, activity_type: str = "memory_operation"):
    """Update agent activity"""
    _agent_registry.update_agent_activity(agent_id, activity_type)

def get_all_active_agents() -> List[Dict[str, Any]]:
    """Get all active agents"""
    return _agent_registry.get_active_agents()

def deregister_agent(agent_id: str) -> Dict[str, Any]:
    """Deregister an agent"""
    return _agent_registry.deregister_agent(agent_id)

# Auto-register this agent (Kiro) when module is imported
def auto_register_kiro():
    """Auto-register Kiro agent"""
    try:
        result = register_agent(
            agent_id="kiro",
            user_id="gabriel",
            agent_type="ai_assistant",
            capabilities=["memory_management", "code_assistance", "multi_agent_coordination"],
            auto_registered=True
        )
        print(f"🤖 Kiro auto-registered: {result.get('message', 'Registration completed')}")
        return result
    except Exception as e:
        print(f"⚠️ Kiro auto-registration failed: {e}")
        return {"error": str(e)}

# Auto-register when imported
if __name__ != "__main__":
    auto_register_kiro()

def test_registration():
    """Test the registration system"""
    print("🧪 Testing Agent Registration System")
    print("=" * 40)
    
    # Test registration
    print("1. Testing agent registration...")
    result1 = register_agent("test_agent", "gabriel", agent_type="test")
    print(f"Registration result: {result1}")
    
    # Test getting session
    print("\n2. Testing session retrieval...")
    session = get_my_session("test_agent")
    print(f"Session: {session}")
    
    # Test activity update
    print("\n3. Testing activity update...")
    update_my_activity("test_agent", "memory_operation")
    
    # Test getting all active agents
    print("\n4. Testing active agents list...")
    active = get_all_active_agents()
    print(f"Active agents: {len(active)}")
    for agent in active:
        print(f"  - {agent['agent_id']}: {agent['memory_count']} memories")
    
    # Test deregistration
    print("\n5. Testing deregistration...")
    dereg_result = deregister_agent("test_agent")
    print(f"Deregistration result: {dereg_result}")
    
    print("\n✅ Registration system test complete!")

if __name__ == "__main__":
    test_registration()