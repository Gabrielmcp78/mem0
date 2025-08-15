#!/usr/bin/env python3
"""
OpenAI API Interceptor - Routes OpenAI calls to Apple Intelligence
This makes mem0 think it's talking to OpenAI but actually uses FoundationModels
Uses only built-in Python modules - no Flask needed!
"""

import sys
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import time

# Add mem0 path
sys.path.insert(0, '/Volumes/Ready500/DEVELOPMENT/mem0')

try:
    from mem0.utils.apple_intelligence import get_foundation_models_interface
    apple_intelligence_available = True
    print("✅ Apple Intelligence available")
except ImportError as e:
    apple_intelligence_available = False
    print(f"❌ Apple Intelligence not available: {e}")

class OpenAIInterceptorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_POST(self):
        """Intercept OpenAI chat completions and route to Apple Intelligence"""
        
        if self.path == '/v1/chat/completions':
            self.handle_chat_completions()
        elif self.path == '/v1/embeddings':
            self.handle_embeddings()
        else:
            self.send_error(404, "Not Found")
    
    def handle_chat_completions(self):
        """Handle chat completions requests"""
        
        if not apple_intelligence_available:
            self.send_json_response({
                "error": {
                    "message": "Apple Intelligence not available",
                    "type": "service_unavailable"
                }
            }, 503)
            return
        
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            messages = data.get('messages', [])
            
            # Convert messages to prompt
            prompt = ""
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role.title()}: {content}\n"
            
            # Get Apple Intelligence interface
            interface = get_foundation_models_interface()
            if not interface or not interface.is_available:
                raise Exception("Apple Intelligence interface not available")
            
            # Generate response
            response_text = interface.generate_text(
                prompt,
                max_tokens=data.get('max_tokens', 1000),
                temperature=data.get('temperature', 0.1)
            )
            
            # Return OpenAI-compatible response
            response = {
                "id": "chatcmpl-apple-intelligence",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "apple-intelligence",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split())
                }
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({
                "error": {
                    "message": str(e),
                    "type": "apple_intelligence_error"
                }
            }, 500)
    
    def handle_embeddings(self):
        """Handle embedding requests - return error for now"""
        self.send_json_response({
            "error": {
                "message": "Use HuggingFace embeddings directly",
                "type": "not_implemented"
            }
        }, 501)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        response_data = json.dumps(data).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_data)

def run_server(port=8888):
    """Run the OpenAI interceptor server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OpenAIInterceptorHandler)
    
    print(f"🚀 OpenAI API Interceptor running on http://localhost:{port}")
    print("   Routes OpenAI calls to Apple Intelligence")
    print("   Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down OpenAI Interceptor")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()