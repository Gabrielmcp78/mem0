#!/usr/bin/env python3
"""
Minimal MCP server to test tool registration
"""

import asyncio
import json
import logging
from typing import List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-server")

class TestMCPServer:
    def __init__(self):
        self.server = Server("test-server")
        self._register_tools()
    
    def _register_tools(self):
        @self.server.call_tool()
        async def ping() -> List[TextContent]:
            """Simple ping tool"""
            return [TextContent(
                type="text",
                text="pong"
            )]
        
        @self.server.call_tool()
        async def echo(message: str) -> List[TextContent]:
            """Echo back a message"""
            return [TextContent(
                type="text",
                text=f"Echo: {message}"
            )]
    
    async def run(self):
        """Run the MCP server"""
        caps = self.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
        logger.info(f"Server capabilities: {caps}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="test-server",
                    server_version="1.0.0",
                    capabilities=caps,
                ),
            )

async def main():
    server = TestMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())