import asyncio
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer
from typing import Dict, List, Callable, Any, Optional, Union
from urllib.parse import parse_qs, urlparse
import threading
import time
import mimetypes
import os
from contextlib import asynccontextmanager


class Request:
    """Request object similar to web framework request"""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes, query_string: str = ""):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_string = query_string
        self.args = parse_qs(query_string)
        self.form = {}
        self.json = None
        
        # Parse form data if present
        if self.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
            self.form = parse_qs(self.body.decode('utf-8'))
        
        # Parse JSON if present
        elif self.headers.get('content-type', '').startswith('application/json'):
            try:
                self.json = json.loads(self.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.json = None


class Response:
    """Response object similar to web framework response"""
    
    def __init__(self, data: Union[str, bytes, dict] = "", status_code: int = 200, 
                 headers: Optional[Dict[str, str]] = None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}
        
        # Set default content type
        if 'content-type' not in self.headers:
            if isinstance(data, dict):
                self.headers['content-type'] = 'application/json'
            elif isinstance(data, str):
                self.headers['content-type'] = 'text/html; charset=utf-8'
            elif isinstance(data, bytes):
                self.headers['content-type'] = 'application/octet-stream'
    
    def to_bytes(self) -> bytes:
        """Convert response to bytes for sending"""
        if isinstance(self.data, dict):
            return json.dumps(self.data).encode('utf-8')
        elif isinstance(self.data, str):
            return self.data.encode('utf-8')
        elif isinstance(self.data, bytes):
            return self.data
        else:
            return str(self.data).encode('utf-8')


class Router:
    """Router for handling URL patterns and route matching"""
    
    def __init__(self):
        self.routes: List[tuple] = []
    
    def add_route(self, method: str, pattern: str, handler: Callable):
        """Add a route with pattern matching"""
        # Convert web-style patterns to regex
        regex_pattern = self._convert_pattern(pattern)
        self.routes.append((method, regex_pattern, handler))
    
    def _convert_pattern(self, pattern: str) -> str:
        """Convert web-style URL patterns to regex patterns"""
        # Replace <type:name> with regex groups
        pattern = re.sub(r'<(\w+):(\w+)>', r'(?P<\2>[^/]+)', pattern)
        # Replace <name> with regex groups (default to string)
        pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)
        # Escape other special characters
        pattern = re.escape(pattern)
        # Restore the regex groups
        pattern = re.sub(r'\\\(\?P<(\w+)>\[\\\^/\]\+\)', r'(?P<\1>[^/]+)', pattern)
        return f'^{pattern}$'
    
    def match_route(self, method: str, path: str) -> Optional[tuple]:
        """Match a route and return handler with parameters"""
        for route_method, pattern, handler in self.routes:
            if route_method == method:
                match = re.match(pattern, path)
                if match:
                    return handler, match.groupdict()
        return None


class AsyncWeb:
    """Main web-like async web framework"""
    
    def __init__(self, name: str = __name__):
        self.name = name
        self.router = Router()
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
        self.static_folder = None
        self.debug = False
    
    def route(self, rule: str, methods: Optional[List[str]] = None):
        """Decorator for adding routes"""
        if methods is None:
            methods = ['GET']
        
        def decorator(f):
            for method in methods:
                self.router.add_route(method.upper(), rule, f)
            return f
        return decorator
    
    def before_request(self, f):
        """Decorator for before request handlers"""
        self.before_request_handlers.append(f)
        return f
    
    def after_request(self, f):
        """Decorator for after request handlers"""
        self.after_request_handlers.append(f)
        return f
    
    def errorhandler(self, code: int):
        """Decorator for error handlers"""
        def decorator(f):
            self.error_handlers[code] = f
            return f
        return decorator
    
    def static_folder(self, folder: str):
        """Set static folder for serving static files"""
        self.static_folder = folder
    
    async def handle_request(self, request: Request) -> Response:
        """Handle an incoming request"""
        try:
            # Run before request handlers
            for handler in self.before_request_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            
            # Match route
            route_match = self.router.match_route(request.method, request.path)
            
            if route_match:
                handler, params = route_match
                
                # Call the route handler
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(request, **params)
                else:
                    result = handler(request, **params)
                
                # Convert result to Response if needed
                if not isinstance(result, Response):
                    result = Response(result)
                
                # Run after request handlers
                for after_handler in self.after_request_handlers:
                    if asyncio.iscoroutinefunction(after_handler):
                        result = await after_handler(result)
                    else:
                        result = after_handler(result)
                
                return result
            else:
                # 404 Not Found
                if 404 in self.error_handlers:
                    handler = self.error_handlers[404]
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(request)
                    else:
                        return handler(request)
                else:
                    return Response("Not Found", 404)
        
        except Exception as e:
            # Handle exceptions
            if self.debug:
                import traceback
                return Response(f"Internal Server Error: {str(e)}\n{traceback.format_exc()}", 500)
            else:
                if 500 in self.error_handlers:
                    handler = self.error_handlers[500]
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(request)
                    else:
                        return handler(request)
                else:
                    return Response("Internal Server Error", 500)
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """Run the development server"""
        self.debug = debug
        
        class AsyncHTTPRequestHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.app = self
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                self._handle_request('GET')
            
            def do_POST(self):
                self._handle_request('POST')
            
            def do_PUT(self):
                self._handle_request('PUT')
            
            def do_DELETE(self):
                self._handle_request('DELETE')
            
            def do_PATCH(self):
                self._handle_request('PATCH')
            
            def _handle_request(self, method):
                # Parse request
                parsed_url = urlparse(self.path)
                path = parsed_url.path
                query_string = parsed_url.query
                
                # Read headers
                headers = {}
                for key, value in self.headers.items():
                    headers[key.lower()] = value
                
                # Read body
                content_length = int(headers.get('content-length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b''
                
                # Create request object
                request = Request(method, path, headers, body, query_string)
                
                # Handle request asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(self.app.handle_request(request))
                finally:
                    loop.close()
                
                # Send response
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.to_bytes())
            
            def log_message(self, format, *args):
                if debug:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")
        
        # Set up server
        server = TCPServer((host, port), AsyncHTTPRequestHandler)
        server.app = self
        
        print(f" * Running on http://{host}:{port}")
        print(f" * Debug mode: {'on' if debug else 'off'}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n * Shutting down server...")
            server.shutdown()


# Global app instance
app = AsyncWeb(__name__)

# Convenience functions
def route(rule: str, methods: Optional[List[str]] = None):
    return app.route(rule, methods)

def before_request(f):
    return app.before_request(f)

def after_request(f):
    return app.after_request(f)

def errorhandler(code: int):
    return app.errorhandler(code)

def run(host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
    return app.run(host, port, debug)
