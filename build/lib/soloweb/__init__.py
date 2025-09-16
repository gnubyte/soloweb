"""
Soloweb - Production-Grade Async Web Framework

A production-grade async web framework for Python that functions like popular web frameworks 
but is async by default and uses zero external dependencies.
"""

__version__ = "1.2.0"
__author__ = "Patrick Hastings"
__description__ = "A production-grade async web framework with zero external dependencies"

import asyncio
import json
import re
import urllib.parse
import hashlib
import hmac
import base64
import time
import secrets
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer
from typing import Dict, List, Callable, Any, Optional, Union
from urllib.parse import parse_qs, urlparse
import threading
import mimetypes
import os
from contextlib import asynccontextmanager
from collections import defaultdict

# Import template engine
try:
    from .templates import Template, render_template as template_render
except ImportError:
    # Fallback if templates module is not available
    def template_render(template_string: str, **context) -> str:
        return f"<h1>Template: {template_string}</h1><p>Context: {context}</p>"


class Blueprint:
    """Blueprint for modular application organization (MVC support)"""
    
    def __init__(self, name: str, url_prefix: str = '', template_folder: str = None, static_folder: str = None):
        self.name = name
        self.url_prefix = url_prefix.rstrip('/')
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.routes: List[tuple] = []
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
        self.middleware: List['Middleware'] = []
        self.app = None
    
    def route(self, rule: str, methods: Optional[List[str]] = None):
        """Decorator for adding routes to the blueprint"""
        if methods is None:
            methods = ['GET']
        
        def decorator(f):
            # Store the route with the blueprint prefix
            full_rule = f"{self.url_prefix}{rule}"
            self.routes.append((methods, full_rule, f))
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
    
    def add_middleware(self, middleware: 'Middleware'):
        """Add middleware to the blueprint"""
        self.middleware.append(middleware)
    
    def register(self, app: 'AsyncWeb'):
        """Register the blueprint with an application"""
        self.app = app
        
        # Register routes
        for methods, rule, handler in self.routes:
            for method in methods:
                app.router.add_route(method.upper(), rule, handler)
        
        # Register before request handlers
        for handler in self.before_request_handlers:
            app.before_request_handlers.append(handler)
        
        # Register after request handlers
        for handler in self.after_request_handlers:
            app.after_request_handlers.append(handler)
        
        # Register error handlers
        for code, handler in self.error_handlers.items():
            app.error_handlers[code] = handler
        
        # Register middleware
        for middleware in self.middleware:
            app.middleware.append(middleware)
    
    def url_for(self, endpoint: str, **kwargs) -> str:
        """Generate URL for endpoint within this blueprint"""
        # Try to find the route for this endpoint in the app's router
        route = self.app.router.get_route_for_endpoint(endpoint)
        if route:
            for key, value in kwargs.items():
                route = route.replace(f'<{key}>', str(value))
                route = route.replace(f'<int:{key}>', str(value))
                route = route.replace(f'<str:{key}>', str(value))
            return route
        # Fallback: just return /<blueprint>/<endpoint>
        return f"{self.url_prefix}/{endpoint}"


class Request:
    """Enhanced Request object similar to web framework request"""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes, query_string: str = ""):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_string = query_string
        self.args = parse_qs(query_string)
        self.form = {}
        self.json = None
        self.files = {}
        self.cookies = self._parse_cookies()
        
        # Parse form data if present
        content_type = self.headers.get('content-type', '')
        if content_type.startswith('application/x-www-form-urlencoded'):
            self.form = parse_qs(self.body.decode('utf-8'))
        elif content_type.startswith('application/json'):
            try:
                self.json = json.loads(self.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.json = None
        elif content_type.startswith('multipart/form-data'):
            self._parse_multipart()
    
    def _parse_cookies(self) -> Dict[str, str]:
        """Parse cookies from headers"""
        cookies = {}
        cookie_header = self.headers.get('cookie', '')
        if cookie_header:
            for cookie in cookie_header.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    cookies[name] = value
        return cookies
    
    def _parse_multipart(self):
        """Parse multipart form data"""
        # Simplified multipart parsing
        boundary = self.headers.get('content-type', '').split('boundary=')[-1]
        if boundary:
            parts = self.body.split(f'--{boundary}'.encode())
            for part in parts[1:-1]:  # Skip first and last parts
                if b'\r\n\r\n' in part:
                    headers_part, data_part = part.split(b'\r\n\r\n', 1)
                    # Extract field name from headers
                    for line in headers_part.decode().split('\r\n'):
                        if line.startswith('Content-Disposition:'):
                            name_match = re.search(r'name="([^"]+)"', line)
                            if name_match:
                                field_name = name_match.group(1)
                                self.form[field_name] = [data_part.rstrip(b'\r\n').decode()]


class Response:
    """Enhanced Response object similar to web framework response"""
    
    def __init__(self, data: Union[str, bytes, dict] = "", status_code: int = 200, 
                 headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}
        self.cookies = cookies or {}
        
        # Set default content type
        if 'content-type' not in self.headers:
            if isinstance(data, dict):
                self.headers['content-type'] = 'application/json'
            elif isinstance(data, str):
                self.headers['content-type'] = 'text/html; charset=utf-8'
            elif isinstance(data, bytes):
                self.headers['content-type'] = 'application/octet-stream'
    
    def set_cookie(self, key: str, value: str, max_age: Optional[int] = None, 
                   expires: Optional[str] = None, path: str = '/', domain: Optional[str] = None,
                   secure: bool = False, httponly: bool = False, samesite: Optional[str] = None):
        """Set a cookie in the response"""
        cookie_parts = [f"{key}={value}"]
        if max_age is not None:
            cookie_parts.append(f"Max-Age={max_age}")
        if expires:
            cookie_parts.append(f"Expires={expires}")
        if path:
            cookie_parts.append(f"Path={path}")
        if domain:
            cookie_parts.append(f"Domain={domain}")
        if secure:
            cookie_parts.append("Secure")
        if httponly:
            cookie_parts.append("HttpOnly")
        if samesite:
            cookie_parts.append(f"SameSite={samesite}")
        
        self.cookies[key] = '; '.join(cookie_parts)
    
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


class Session:
    """Simple session implementation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        self.sessions = {}
    
    def create_session(self, data: dict) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        timestamp = str(int(time.time()))
        session_data = {
            'data': data,
            'timestamp': timestamp
        }
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            # Check if session is expired (24 hours)
            if int(time.time()) - int(session_data['timestamp']) < 86400:
                return session_data['data']
            else:
                del self.sessions[session_id]
        return None
    
    def update_session(self, session_id: str, data: dict):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]['data'] = data
            self.sessions[session_id]['timestamp'] = str(int(time.time()))
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


class Router:
    """Enhanced Router for handling URL patterns and route matching"""
    
    def __init__(self):
        self.routes: List[tuple] = []
        self.endpoints: Dict[str, str] = {}  # endpoint -> route mapping
    
    def add_route(self, method: str, pattern: str, handler: Callable):
        """Add a route with pattern matching"""
        # Convert web-style patterns to regex
        regex_pattern = self._convert_pattern(pattern)
        self.routes.append((method, regex_pattern, handler))
        
        # Store endpoint mapping for url_for
        handler_name = handler.__name__
        self.endpoints[handler_name] = pattern
    
    def _convert_pattern(self, pattern: str) -> str:
        """Convert web-style URL patterns to regex patterns"""
        def replacer(match):
            type_ = match.group(1)
            name = match.group(2)
            if type_ == 'int':
                return f'(?P<{name}>\\d+)'
            elif type_ == 'str' or type_ is None:
                return f'(?P<{name}>[^/]+)'
            else:
                return f'(?P<{name}>[^/]+)'
        # Match <type:name> or <name>
        pattern = re.sub(r'<(?:(int|str):)?(\w+)>', replacer, pattern)
        return f'^{pattern}$'
    
    def match_route(self, method: str, path: str) -> Optional[tuple]:
        """Match a route and return handler with parameters"""
        for route_method, pattern, handler in self.routes:
            if route_method == method:
                match = re.match(pattern, path)
                if match:
                    return handler, match.groupdict()
        return None
    
    def get_route_for_endpoint(self, endpoint: str) -> Optional[str]:
        """Get route pattern for an endpoint"""
        return self.endpoints.get(endpoint)


class Middleware:
    """Middleware base class"""
    
    async def process_request(self, request: Request) -> Optional[Response]:
        """Process request before it reaches the route handler"""
        return None
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process response after it's generated"""
        return response


class CORSMiddleware(Middleware):
    """CORS middleware"""
    
    def __init__(self, origins: List[str] = None, methods: List[str] = None, headers: List[str] = None):
        self.origins = origins or ['*']
        self.methods = methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.headers = headers or ['Content-Type', 'Authorization']
    
    async def process_request(self, request: Request) -> Optional[Response]:
        if request.method == 'OPTIONS':
            return Response("", 200, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': ', '.join(self.methods),
                'Access-Control-Allow-Headers': ', '.join(self.headers)
            })
        return None
    
    async def process_response(self, request: Request, response: Response) -> Response:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = ', '.join(self.methods)
        response.headers['Access-Control-Allow-Headers'] = ', '.join(self.headers)
        return response


class AsyncWeb:
    """Enhanced web-like async web framework with blueprint support"""
    
    def __init__(self, name: str = __name__, secret_key: Optional[str] = None):
        self.name = name
        self.router = Router()
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
        self.middleware: List[Middleware] = []
        self.static_folder = None
        self.debug = False
        self.secret_key = secret_key or secrets.token_hex(32)
        self.session = Session(self.secret_key)
        self.blueprints: Dict[str, Blueprint] = {}
    
    def register_blueprint(self, blueprint: Blueprint):
        """Register a blueprint with the application"""
        if blueprint.name in self.blueprints:
            raise ValueError(f"Blueprint '{blueprint.name}' is already registered")
        
        self.blueprints[blueprint.name] = blueprint
        blueprint.register(self)
    
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
    
    def add_middleware(self, middleware: Middleware):
        """Add middleware to the application"""
        self.middleware.append(middleware)
    
    def static_folder(self, folder: str):
        """Set static folder for serving static files"""
        self.static_folder = folder
    
    def url_for(self, endpoint: str, **kwargs) -> str:
        """Generate URL for endpoint with blueprint support"""
        # Handle blueprint endpoints (blueprint.endpoint)
        if '.' in endpoint:
            blueprint_name, endpoint_name = endpoint.split('.', 1)
            if blueprint_name in self.blueprints:
                blueprint = self.blueprints[blueprint_name]
                return blueprint.url_for(endpoint_name, **kwargs)
        
        # Handle regular endpoints
        route = self.router.get_route_for_endpoint(endpoint)
        if route:
            # Simple parameter substitution (basic implementation)
            for key, value in kwargs.items():
                route = route.replace(f'<{key}>', str(value))
            return route
        
        return f"/{endpoint}"
    
    def redirect(self, location: str, code: int = 302) -> Response:
        """Create a redirect response"""
        return Response("", code, headers={'Location': location})
    
    def jsonify(self, data: Any) -> Response:
        """Create a JSON response"""
        return Response(data, headers={'Content-Type': 'application/json'})
    
    def render_template(self, template_name: str, **context) -> str:
        """Render a template with the given context"""
        # For now, we'll use the template string directly
        # In a full implementation, you'd load templates from files
        template_string = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title | default('Soloweb App') }}</title>
        </head>
        <body>
            <h1>{{ title | default('Welcome') }}</h1>
            <div class="content">
                {{ content | default('No content provided') }}
            </div>
            {% if user %}
            <div class="user-info">
                <p>Welcome, {{ user.name | default(user) }}!</p>
            </div>
            {% endif %}
            {% if items %}
            <ul>
                {% for item in items %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </body>
        </html>
        """
        
        # Add template_name to context for debugging
        context['template_name'] = template_name
        return template_render(template_string, **context)
    
    async def handle_request(self, request: Request) -> Response:
        """Handle an incoming request"""
        try:
            # Process middleware
            for middleware in self.middleware:
                middleware_response = await middleware.process_request(request)
                if middleware_response:
                    return middleware_response
            
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
                
                # Process middleware
                for middleware in self.middleware:
                    result = await middleware.process_response(request, result)
                
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
            
            def do_OPTIONS(self):
                self._handle_request('OPTIONS')
            
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
                
                # Set cookies
                for key, value in response.cookies.items():
                    self.send_header('Set-Cookie', value)
                
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

def jsonify(data: Any) -> Response:
    return app.jsonify(data)

def redirect(location: str, code: int = 302) -> Response:
    return app.redirect(location, code)

def url_for(endpoint: str, **kwargs) -> str:
    return app.url_for(endpoint, **kwargs)

def create_blueprint(name: str, url_prefix: str = '', template_folder: str = None, static_folder: str = None):
    return Blueprint(name, url_prefix, template_folder, static_folder) 