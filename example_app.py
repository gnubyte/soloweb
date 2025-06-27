#!/usr/bin/env python3
"""
Example application demonstrating the Soloweb framework
This shows all the major features including async routes, middleware, sessions, etc.
"""

import asyncio
import time
from soloweb import (
    app, route, before_request, after_request, errorhandler, 
    run, jsonify, redirect, url_for, CORSMiddleware, Response
)


# Add CORS middleware
app.add_middleware(CORSMiddleware())


# Before request handler - runs before every request
@before_request
async def log_request():
    print(f"[{time.strftime('%H:%M:%S')}] Request started")


# After request handler - runs after every request
@after_request
async def add_timing_header(response):
    response.headers['X-Response-Time'] = str(time.time())
    return response


# Error handlers
@errorhandler(404)
async def not_found(request):
    return Response("""
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/">Go back home</a>
    """, 404)


@errorhandler(500)
async def internal_error(request):
    return Response("""
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong on our end.</p>
    <a href="/">Go back home</a>
    """, 500)


# Basic routes
@route('/')
async def home(request):
    return """
    <h1>Welcome to Soloweb!</h1>
    <p>This is a production-grade async web framework built with zero external dependencies.</p>
    
    <h2>Available endpoints:</h2>
    <ul>
        <li><a href="/hello">/hello</a> - Basic greeting</li>
        <li><a href="/hello/World">/hello/World</a> - Parameterized greeting</li>
        <li><a href="/api/users">/api/users</a> - JSON API endpoint</li>
        <li><a href="/session">/session</a> - Session management</li>
        <li><a href="/async-demo">/async-demo</a> - Async operations demo</li>
        <li><a href="/form">/form</a> - Form handling</li>
        <li><a href="/redirect-demo">/redirect-demo</a> - Redirect demo</li>
        <li><a href="/error-demo">/error-demo</a> - Error handling demo</li>
    </ul>
    
    <h2>Features:</h2>
    <ul>
        <li>✅ Async by default</li>
        <li>✅ Zero external dependencies</li>
        <li>✅ Flask-like API</li>
        <li>✅ Middleware support</li>
        <li>✅ Session management</li>
        <li>✅ Error handling</li>
        <li>✅ CORS support</li>
        <li>✅ Cookie handling</li>
        <li>✅ JSON support</li>
        <li>✅ Form data parsing</li>
    </ul>
    """


@route('/hello')
async def hello(request):
    return "<h1>Hello, World!</h1><p>This is an async route.</p>"


@route('/hello/<name>')
async def hello_name(request, name):
    return f"<h1>Hello, {name}!</h1><p>Welcome to Soloweb.</p>"


# JSON API endpoints
@route('/api/users')
async def api_users(request):
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]
    return jsonify(users)


@route('/api/users/<user_id>')
async def api_user(request, user_id):
    try:
        user_id = int(user_id)
        users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
            3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        }
        
        if user_id in users:
            return jsonify(users[user_id])
        else:
            return jsonify({"error": "User not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400


# Session management
@route('/session')
async def session_demo(request):
    # Get session ID from cookie
    session_id = request.cookies.get('session_id')
    
    if session_id:
        # Get existing session data
        session_data = app.session.get_session(session_id)
        if session_data:
            visit_count = session_data.get('visit_count', 0) + 1
            session_data['visit_count'] = visit_count
            app.session.update_session(session_id, session_data)
        else:
            # Session expired, create new one
            session_data = {'visit_count': 1}
            session_id = app.session.create_session(session_data)
    else:
        # No session, create new one
        session_data = {'visit_count': 1}
        session_id = app.session.create_session(session_data)
    
    response = Response(f"""
    <h1>Session Demo</h1>
    <p>Session ID: {session_id}</p>
    <p>Visit count: {session_data['visit_count']}</p>
    <p>Session data: {session_data}</p>
    <a href="/session">Refresh to increment counter</a>
    """)
    
    # Set session cookie
    response.set_cookie('session_id', session_id, max_age=3600, httponly=True)
    return response


# Async operations demo
@route('/async-demo')
async def async_demo(request):
    # Simulate multiple async operations
    start_time = time.time()
    
    # Run multiple async tasks concurrently
    tasks = [
        simulate_async_operation("Database query", 0.5),
        simulate_async_operation("API call", 0.3),
        simulate_async_operation("File I/O", 0.2),
        simulate_async_operation("Cache lookup", 0.1)
    ]
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    html = f"""
    <h1>Async Operations Demo</h1>
    <p>Total time: {total_time:.3f} seconds</p>
    <p>If this were synchronous, it would take: {sum(r['duration'] for r in results):.3f} seconds</p>
    
    <h2>Results:</h2>
    <ul>
    """
    
    for result in results:
        html += f"<li>{result['operation']}: {result['duration']:.3f}s</li>"
    
    html += """
    </ul>
    <p><strong>Note:</strong> All operations ran concurrently, demonstrating true async behavior!</p>
    """
    
    return html


async def simulate_async_operation(operation: str, duration: float):
    """Simulate an async operation"""
    await asyncio.sleep(duration)
    return {
        'operation': operation,
        'duration': duration,
        'result': f'Completed {operation}'
    }


# Form handling
@route('/form', methods=['GET'])
async def show_form(request):
    return """
    <h1>Form Demo</h1>
    <form method="POST" action="/form">
        <p>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
        </p>
        <p>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </p>
        <p>
            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="4" cols="50"></textarea>
        </p>
        <p>
            <button type="submit">Submit</button>
        </p>
    </form>
    """


@route('/form', methods=['POST'])
async def handle_form(request):
    name = request.form.get('name', [''])[0]
    email = request.form.get('email', [''])[0]
    message = request.form.get('message', [''])[0]
    
    return f"""
    <h1>Form Submitted!</h1>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Message:</strong> {message}</p>
    <p><a href="/form">Submit another form</a></p>
    """


# JSON API with POST
@route('/api/submit', methods=['POST'])
async def api_submit(request):
    if request.json:
        data = request.json
        return jsonify({
            "status": "success",
            "message": "Data received successfully",
            "data": data
        })
    else:
        return jsonify({"error": "No JSON data provided"}), 400


# Redirect demo
@route('/redirect-demo')
async def redirect_demo(request):
    return """
    <h1>Redirect Demo</h1>
    <p>This page demonstrates redirects:</p>
    <ul>
        <li><a href="/redirect-to-home">Redirect to home</a></li>
        <li><a href="/redirect-to-hello">Redirect to hello</a></li>
        <li><a href="/permanent-redirect">Permanent redirect</a></li>
    </ul>
    """


@route('/redirect-to-home')
async def redirect_to_home(request):
    return redirect('/')


@route('/redirect-to-hello')
async def redirect_to_hello(request):
    return redirect('/hello')


@route('/permanent-redirect')
async def permanent_redirect(request):
    return redirect('/hello', 301)


# Error demo
@route('/error-demo')
async def error_demo(request):
    return """
    <h1>Error Handling Demo</h1>
    <p>Test different error scenarios:</p>
    <ul>
        <li><a href="/trigger-404">Trigger 404</a></li>
        <li><a href="/trigger-500">Trigger 500</a></li>
        <li><a href="/trigger-custom">Trigger custom error</a></li>
    </ul>
    """


@route('/trigger-404')
async def trigger_404(request):
    # This will trigger the 404 error handler
    raise Exception("This route doesn't exist")


@route('/trigger-500')
async def trigger_500(request):
    # This will trigger the 500 error handler
    raise Exception("Internal server error simulation")


@route('/trigger-custom')
async def trigger_custom(request):
    return Response("Custom error message", 418, headers={'X-Custom-Error': 'I\'m a teapot'})


# Performance test endpoint
@route('/performance-test')
async def performance_test(request):
    start_time = time.time()
    
    # Simulate some async work
    await asyncio.sleep(0.1)
    
    processing_time = time.time() - start_time
    
    return jsonify({
        "status": "success",
        "processing_time": processing_time,
        "timestamp": time.time(),
        "message": "Performance test completed"
    })


# Health check endpoint
@route('/health')
async def health_check(request):
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "framework": "Soloweb",
        "version": "1.0.0"
    })


if __name__ == '__main__':
    print("Starting Soloweb Example Application...")
    print("=" * 50)
    print("Features demonstrated:")
    print("- Async route handlers")
    print("- Middleware (CORS)")
    print("- Session management")
    print("- Error handling")
    print("- Form processing")
    print("- JSON API endpoints")
    print("- Redirects")
    print("- Before/after request hooks")
    print("=" * 50)
    
    # Run the application
    run(host='127.0.0.1', port=5000, debug=True) 