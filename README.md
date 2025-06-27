# Soloweb - Production-Grade Async Web Framework

A production-grade async web framework for Python that functions exactly like Flask but is async by default and uses **zero external dependencies**. Built entirely with standard Python libraries.

## 🚀 Features

- **Async by Default**: All route handlers are async and support concurrent operations
- **Zero Dependencies**: Uses only standard Python libraries (no pip install required)
- **Flask-like API**: Familiar decorators and patterns for Flask developers
- **Production Ready**: Includes middleware, sessions, error handling, and more
- **Type Hints**: Full type annotation support for better development experience
- **CORS Support**: Built-in CORS middleware for cross-origin requests
- **Session Management**: Secure session handling with configurable expiration
- **Error Handling**: Custom error handlers for different HTTP status codes
- **Cookie Support**: Full cookie parsing and setting capabilities
- **JSON Support**: Automatic JSON request/response handling
- **Form Processing**: Support for form data and multipart uploads
- **URL Routing**: Dynamic URL parameters with type conversion
- **Before/After Hooks**: Request and response middleware support

## 📦 Installation

### From PyPI (when available)
```bash
pip install soloweb
```

### From GitHub Releases
```bash
# Install specific version
pip install https://github.com/gnubyte/soloweb/releases/download/v1.2.0/soloweb-1.2.0-py3-none-any.whl

# Or install from source
pip install git+https://github.com/gnubyte/soloweb.git@v1.2.0
```

### Manual Installation
No installation required! Just copy the framework files to your project:

```bash
# Copy the framework files
cp soloweb.py your_project/
```
## 🎯 Quick Start

```python
from soloweb import app, route, run

@route('/')
async def home(request):
    return "<h1>Hello, Soloweb!</h1>"

@route('/api/users')
async def get_users(request):
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    return {"users": users}

if __name__ == '__main__':
    run(debug=True)
```

## 📚 API Reference

### Core Classes

#### AsyncFlask

The main application class.

```python
app = AsyncFlask(name="my_app", secret_key="your-secret-key")
```

**Parameters:**
- `name`: Application name (default: `__name__`)
- `secret_key`: Secret key for sessions (auto-generated if not provided)

#### Request

Request object containing all request data.

```python
# Available attributes
request.method          # HTTP method (GET, POST, etc.)
request.path           # Request path
request.headers        # Request headers
request.body           # Raw request body
request.args           # Query parameters
request.form           # Form data
request.json           # JSON data
request.cookies        # Request cookies
```

#### Response

Response object for sending data back to clients.

```python
response = Response(
    data="Hello World",
    status_code=200,
    headers={"Content-Type": "text/html"},
    cookies={"session_id": "abc123"}
)
```

### Decorators

#### @route()

Define URL routes with HTTP methods.

```python
@route('/users/<user_id>', methods=['GET', 'POST'])
async def user_handler(request, user_id):
    return f"User ID: {user_id}"
```

**Parameters:**
- `rule`: URL pattern (supports Flask-style parameters like `<name>`)
- `methods`: List of HTTP methods (default: `['GET']`)

#### @before_request

Register functions to run before each request.

```python
@before_request
async def log_request():
    print(f"Request started at {time.time()}")
```

#### @after_request

Register functions to run after each request.

```python
@after_request
async def add_header(response):
    response.headers['X-Custom-Header'] = 'value'
    return response
```

#### @errorhandler

Register custom error handlers.

```python
@errorhandler(404)
async def not_found(request):
    return Response("Page not found", 404)
```

### Utility Functions

#### jsonify()

Create JSON responses.

```python
@route('/api/data')
async def get_data(request):
    return jsonify({"status": "success", "data": [1, 2, 3]})
```

#### redirect()

Create redirect responses.

```python
@route('/old-page')
async def old_page(request):
    return redirect('/new-page', 301)
```

#### url_for()

Generate URLs for endpoints (simplified implementation).

```python
url = url_for('user_profile', user_id=123)
```

### Middleware

#### CORSMiddleware

Handle Cross-Origin Resource Sharing.

```python
from soloweb import CORSMiddleware

app.add_middleware(CORSMiddleware(
    origins=['http://localhost:3000'],
    methods=['GET', 'POST', 'PUT', 'DELETE'],
    headers=['Content-Type', 'Authorization']
))
```

#### Custom Middleware

Create custom middleware by inheriting from `Middleware`.

```python
class LoggingMiddleware(Middleware):
    async def process_request(self, request):
        print(f"Processing {request.method} {request.path}")
        return None
    
    async def process_response(self, request, response):
        print(f"Response status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware())
```

### Session Management

```python
# Create a session
session_data = {"user_id": 123, "username": "alice"}
session_id = app.session.create_session(session_data)

# Get session data
data = app.session.get_session(session_id)

# Update session
app.session.update_session(session_id, {"user_id": 456})

# Delete session
app.session.delete_session(session_id)
```

## 🔧 Configuration

### Running the Server

```python
# Basic usage
run()

# With custom settings
run(
    host='0.0.0.0',      # Bind to all interfaces
    port=8080,           # Custom port
    debug=True           # Enable debug mode
)
```

### Debug Mode

When debug mode is enabled:
- Detailed error messages are shown
- Request logging is enabled
- Stack traces are displayed for exceptions

```python
run(debug=True)
```

## 📝 Examples

### Basic Web Application

```python
from soloweb import app, route, run, jsonify

@route('/')
async def home(request):
    return """
    <h1>Welcome to Soloweb</h1>
    <p>This is a production-grade async web framework!</p>
    """

@route('/api/status')
async def status(request):
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    run(debug=True)
```

### REST API

```python
from soloweb import app, route, jsonify, Response

# In-memory storage for demo
users = {}

@route('/api/users', methods=['GET'])
async def get_users(request):
    return jsonify(list(users.values()))

@route('/api/users/<user_id>', methods=['GET'])
async def get_user(request, user_id):
    if user_id in users:
        return jsonify(users[user_id])
    return jsonify({"error": "User not found"}), 404

@route('/api/users', methods=['POST'])
async def create_user(request):
    if not request.json:
        return jsonify({"error": "No JSON data"}), 400
    
    user_id = str(len(users) + 1)
    users[user_id] = {
        "id": user_id,
        **request.json
    }
    return jsonify(users[user_id]), 201

@route('/api/users/<user_id>', methods=['PUT'])
async def update_user(request, user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    if not request.json:
        return jsonify({"error": "No JSON data"}), 400
    
    users[user_id].update(request.json)
    return jsonify(users[user_id])

@route('/api/users/<user_id>', methods=['DELETE'])
async def delete_user(request, user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    del users[user_id]
    return Response("", 204)
```

### Form Handling

```python
@route('/form', methods=['GET'])
async def show_form(request):
    return """
    <form method="POST">
        <input type="text" name="name" placeholder="Name" required>
        <input type="email" name="email" placeholder="Email" required>
        <button type="submit">Submit</button>
    </form>
    """

@route('/form', methods=['POST'])
async def handle_form(request):
    name = request.form.get('name', [''])[0]
    email = request.form.get('email', [''])[0]
    
    return f"""
    <h1>Form Submitted!</h1>
    <p>Name: {name}</p>
    <p>Email: {email}</p>
    """
```

### Session Management

```python
@route('/login')
async def login(request):
    # Create session for user
    session_data = {"user_id": 123, "username": "alice"}
    session_id = app.session.create_session(session_data)
    
    response = Response("Logged in successfully!")
    response.set_cookie('session_id', session_id, max_age=3600, httponly=True)
    return response

@route('/profile')
async def profile(request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect('/login')
    
    session_data = app.session.get_session(session_id)
    if not session_data:
        return redirect('/login')
    
    return f"""
    <h1>Profile</h1>
    <p>Welcome, {session_data['username']}!</p>
    """
```

## 🧪 Testing

Run the test suite to verify the framework works correctly:

```bash
python test_framework.py
```

## 🚀 Performance

The framework is designed for high performance:

- **Async by default**: All operations are non-blocking
- **Concurrent handling**: Multiple requests can be processed simultaneously
- **Minimal overhead**: Zero external dependencies mean faster startup
- **Efficient routing**: Regex-based route matching for fast lookups

## 🔒 Security Features

- **Session security**: Secure session IDs with expiration
- **Cookie security**: HttpOnly and Secure cookie options
- **CORS protection**: Configurable cross-origin request handling
- **Error handling**: Safe error responses without information leakage

## 📋 Requirements

- Python 3.7+ (for async/await support)
- No external dependencies required

## 🤝 Contributing

This is a standalone framework, but you can extend it by:

1. Adding new middleware classes
2. Implementing additional utility functions
3. Creating custom request/response handlers
4. Adding template engine support

## 📄 License

This framework is provided as-is for educational and production use.

## 🎯 Comparison with Flask

| Feature | Flask | Soloweb |
|---------|-------|---------|
| Async Support | ❌ | ✅ |
| Dependencies | Many | Zero |
| Performance | Good | Excellent |
| API Compatibility | Reference | Similar |
| Learning Curve | Low | Low |
| Production Ready | ✅ | ✅ |

## 🚀 Getting Started

1. Copy `soloweb.py` to your project
2. Create your application file
3. Define your routes with `@route()` decorators
4. Run with `run()` function

```python
# app.py
from soloweb import app, route, run

@route('/')
async def hello(request):
    return "Hello, Soloweb World!"

if __name__ == '__main__':
    run(debug=True)
```

Then run:
```bash
python app.py
```

Visit `http://localhost:5000` to see your application running!

---

**Built with ❤️ using only standard Python libraries** # soloweb
