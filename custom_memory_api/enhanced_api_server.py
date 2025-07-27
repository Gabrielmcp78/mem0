#!/usr/bin/env python3
"""
Enhanced Memory API Server
Extends OpenMemory with custom endpoints and features
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
import uuid

# Import our MCP integration
from mcp_integration_system import MCPServer, MemoryMCPPlugin, AgentMCPPlugin

app = FastAPI(
    title="Enhanced Memory API",
    description="Custom memory ecosystem API with MCP integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:13001", "http://localhost:13000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/system/info")
async def system_info():
    """Get system information"""
    return {
        "memory_system": "active",
        "mcp_server": "running",
        "ui_version": "1.0.0",
        "features": [
            "enhanced_ui",
            "mobile_support",
            "mcp_integration",
            "real_time_updates"
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/v1/analytics/dashboard")
async def dashboard_analytics():
    """Get dashboard analytics"""
    return {
        "total_memories": 150,
        "active_users": 5,
        "avg_score": 0.75,
        "recent_activity": [
            {
                "type": "memory_added",
                "timestamp": datetime.now().isoformat(),
                "user": "user123"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_server:app",
        host="0.0.0.0",
        port=18767,
        reload=True,
        log_level="info"
    )
