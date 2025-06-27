#!/usr/bin/env python3
"""
Soloweb Framework - Complete Guide & Best Practices

This file demonstrates how to effectively use the Soloweb framework for building
production-ready async web applications. It covers:

1. Basic Setup & Configuration
2. Blueprint Patterns for MVC Architecture
3. Template Engine Usage
4. Authentication & Authorization
5. API Development
6. Error Handling & Middleware
7. Database Integration Patterns
8. Testing Strategies

Key Features Demonstrated:
- Zero external dependencies
- Async by default
- Flask-like syntax
- Blueprint support for modular apps
- Jinja-like template engine
- Built-in session management
- CORS middleware
- Comprehensive error handling
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from soloweb import (
    AsyncFlask, Blueprint, Request, Response, 
    CORSMiddleware, render_template, jsonify, redirect, url_for
)


# ============================================================================
# 1. APPLICATION SETUP & CONFIGURATION
# ============================================================================

def create_app(config: Dict[str, Any] = None) -> AsyncFlask:
    """
    Application factory pattern - recommended for production apps.
    Allows for different configurations (dev, test, prod).
    """
    app = AsyncFlask(__name__, secret_key="your-secret-key-here")
    
    # Configuration
    app.debug = config.get('debug', False) if config else False
    
    # Add middleware
    app.add_middleware(CORSMiddleware(
        origins=['http://localhost:3000', 'https://yourdomain.com'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        headers=['Content-Type', 'Authorization']
    ))
    
    # Global error handlers
    @app.errorhandler(404)
    async def not_found(request):
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>Page Not Found</title></head>
        <body>
            <h1>404 - Page Not Found</h1>
            <p>The requested page could not be found.</p>
            <a href="/">Go Home</a>
        </body>
        </html>
        """, status_code=404)
    
    @app.errorhandler(500)
    async def server_error(request):
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>Server Error</title></head>
        <body>
            <h1>500 - Internal Server Error</h1>
            <p>Something went wrong on our end.</p>
            <a href="/">Go Home</a>
        </body>
        </html>
        """, status_code=500)
    
    # Global before_request handler
    @app.before_request
    async def before_request():
        # Add request timing, logging, etc.
        pass
    
    # Global after_request handler
    @app.after_request
    async def after_request(response):
        # Add headers, logging, etc.
        response.headers['X-Powered-By'] = 'Soloweb'
        return response
    
    return app


# ============================================================================
# 2. BLUEPRINT PATTERNS - MVC ARCHITECTURE
# ============================================================================

# Auth Blueprint - Authentication & Authorization
auth_bp = Blueprint('auth', url_prefix='/auth')

@auth_bp.before_request
async def auth_before_request():
    """Global auth middleware for all auth routes"""
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
async def login(request):
    if request.method == 'GET':
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login</h1>
            <form method="POST">
                <div>
                    <label>Email: <input type="email" name="email" required></label>
                </div>
                <div>
                    <label>Password: <input type="password" name="password" required></label>
                </div>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """)
    
    # Handle POST login
    email = request.form.get('email', [''])[0]
    password = request.form.get('password', [''])[0]
    
    # Simple authentication (replace with real auth)
    if email == 'admin@example.com' and password == 'password':
        # Create session
        session_data = {
            'user_id': 1,
            'email': email,
            'role': 'admin',
            'login_time': datetime.now().isoformat()
        }
        session_id = request.app.session.create_session(session_data)
        
        response = redirect('/dashboard')
        response.set_cookie('session_id', session_id, max_age=3600)
        return response
    
    return render_template("""
    <!DOCTYPE html>
    <html>
    <head><title>Login Failed</title></head>
    <body>
        <h1>Login Failed</h1>
        <p>Invalid credentials. <a href="/auth/login">Try again</a></p>
    </body>
    </html>
    """, status_code=401)

@auth_bp.route('/logout')
async def logout(request):
    session_id = request.cookies.get('session_id')
    if session_id:
        request.app.session.delete_session(session_id)
    
    response = redirect('/')
    response.set_cookie('session_id', '', max_age=0)
    return response

@auth_bp.route('/register', methods=['GET', 'POST'])
async def register(request):
    if request.method == 'GET':
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>Register</title></head>
        <body>
            <h1>Register</h1>
            <form method="POST">
                <div>
                    <label>Name: <input type="text" name="name" required></label>
                </div>
                <div>
                    <label>Email: <input type="email" name="email" required></label>
                </div>
                <div>
                    <label>Password: <input type="password" name="password" required></label>
                </div>
                <button type="submit">Register</button>
            </form>
        </body>
        </html>
        """)
    
    # Handle registration (simplified)
    return redirect('/auth/login')


# Users Blueprint - User Management
users_bp = Blueprint('users', url_prefix='/users')

@users_bp.route('/')
async def list_users(request):
    """List all users (admin only)"""
    # Check authentication
    user = get_current_user(request)
    if not user or user.get('role') != 'admin':
        return redirect('/auth/login')
    
    # Mock user data
    users = [
        {'id': 1, 'name': 'Alice Smith', 'email': 'alice@example.com', 'role': 'admin'},
        {'id': 2, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'role': 'user'},
        {'id': 3, 'name': 'Charlie Brown', 'email': 'charlie@example.com', 'role': 'user'},
    ]
    
    return render_template("""
    <!DOCTYPE html>
    <html>
    <head><title>Users</title></head>
    <body>
        <h1>Users</h1>
        <table border="1">
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th></tr>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role | upper }}</td>
            </tr>
            {% endfor %}
        </table>
        <p><a href="/dashboard">Back to Dashboard</a></p>
    </body>
    </html>
    """, users=users)

@users_bp.route('/<int:user_id>')
async def get_user(request, user_id):
    """Get specific user details"""
    user = get_current_user(request)
    if not user:
        return redirect('/auth/login')
    
    # Mock user data
    user_data = {
        'id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com',
        'role': 'user',
        'created_at': '2024-01-01',
        'last_login': '2024-01-15'
    }
    
    return render_template("""
    <!DOCTYPE html>
    <html>
    <head><title>User Profile</title></head>
    <body>
        <h1>User Profile</h1>
        <div>
            <p><strong>ID:</strong> {{ user.id }}</p>
            <p><strong>Name:</strong> {{ user.name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Role:</strong> {{ user.role | title }}</p>
            <p><strong>Created:</strong> {{ user.created_at }}</p>
            <p><strong>Last Login:</strong> {{ user.last_login }}</p>
        </div>
        <p><a href="/users">Back to Users</a></p>
    </body>
    </html>
    """, user=user_data)


# API Blueprint - RESTful API
api_bp = Blueprint('api', url_prefix='/api/v1')

@api_bp.before_request
async def api_before_request():
    """API-specific middleware"""
    pass

@api_bp.route('/users', methods=['GET'])
async def api_list_users(request):
    """API endpoint to list users"""
    users = [
        {'id': 1, 'name': 'Alice Smith', 'email': 'alice@example.com'},
        {'id': 2, 'name': 'Bob Johnson', 'email': 'bob@example.com'},
    ]
    return jsonify({'users': users, 'count': len(users)})

@api_bp.route('/users/<int:user_id>', methods=['GET'])
async def api_get_user(request, user_id):
    """API endpoint to get specific user"""
    user = {'id': user_id, 'name': f'User {user_id}', 'email': f'user{user_id}@example.com'}
    return jsonify({'user': user})

@api_bp.route('/users', methods=['POST'])
async def api_create_user(request):
    """API endpoint to create user"""
    if not request.json:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    user_data = request.json
    # Validate required fields
    if not user_data.get('name') or not user_data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    # Mock user creation
    new_user = {
        'id': 999,
        'name': user_data['name'],
        'email': user_data['email'],
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'user': new_user, 'message': 'User created successfully'}), 201

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
async def api_update_user(request, user_id):
    """API endpoint to update user"""
    if not request.json:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Mock user update
    updated_user = {
        'id': user_id,
        'name': request.json.get('name', f'User {user_id}'),
        'email': request.json.get('email', f'user{user_id}@example.com'),
        'updated_at': datetime.now().isoformat()
    }
    
    return jsonify({'user': updated_user, 'message': 'User updated successfully'})

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
async def api_delete_user(request, user_id):
    """API endpoint to delete user"""
    return jsonify({'message': f'User {user_id} deleted successfully'})


# Admin Blueprint - Administration Panel
admin_bp = Blueprint('admin', url_prefix='/admin')

@admin_bp.before_request
async def admin_before_request():
    """Admin authentication middleware"""
    user = get_current_user(request)
    if not user or user.get('role') != 'admin':
        return redirect('/auth/login')

@admin_bp.route('/dashboard')
async def admin_dashboard(request):
    """Admin dashboard"""
    stats = {
        'total_users': 1250,
        'active_users': 342,
        'total_posts': 89,
        'system_health': 'Good'
    }
    
    return render_template("""
    <!DOCTYPE html>
    <html>
    <head><title>Admin Dashboard</title></head>
    <body>
        <h1>Admin Dashboard</h1>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
            <div style="border: 1px solid #ccc; padding: 20px;">
                <h3>System Statistics</h3>
                <p><strong>Total Users:</strong> {{ stats.total_users }}</p>
                <p><strong>Active Users:</strong> {{ stats.active_users }}</p>
                <p><strong>Total Posts:</strong> {{ stats.total_posts }}</p>
                <p><strong>System Health:</strong> {{ stats.system_health }}</p>
            </div>
            <div style="border: 1px solid #ccc; padding: 20px;">
                <h3>Quick Actions</h3>
                <ul>
                    <li><a href="/users">Manage Users</a></li>
                    <li><a href="/admin/settings">System Settings</a></li>
                    <li><a href="/admin/logs">View Logs</a></li>
                </ul>
            </div>
        </div>
        <p><a href="/dashboard">Back to Main Dashboard</a></p>
    </body>
    </html>
    """, stats=stats)


# ============================================================================
# 3. HELPER FUNCTIONS & UTILITIES
# ============================================================================

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from session"""
    session_id = request.cookies.get('session_id')
    if session_id:
        return request.app.session.get_session(session_id)
    return None

def require_auth(f):
    """Decorator to require authentication"""
    async def decorated(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect('/auth/login')
        return await f(request, *args, **kwargs)
    return decorated

def require_admin(f):
    """Decorator to require admin role"""
    async def decorated(request, *args, **kwargs):
        user = get_current_user(request)
        if not user or user.get('role') != 'admin':
            return redirect('/auth/login')
        return await f(request, *args, **kwargs)
    return decorated


# ============================================================================
# 4. MAIN APPLICATION ROUTES
# ============================================================================

def setup_main_routes(app: AsyncFlask):
    """Setup main application routes"""
    
    @app.route('/')
    async def home(request):
        """Home page"""
        user = get_current_user(request)
        
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Soloweb Framework</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                .nav { margin: 20px 0; }
                .nav a { margin-right: 15px; color: #3498db; text-decoration: none; }
                .feature { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Soloweb Framework</h1>
                    {% if user %}
                    <p>Hello, {{ user.email }}! ({{ user.role | title }})</p>
                    {% else %}
                    <p>A production-grade async web framework with zero external dependencies</p>
                    {% endif %}
                </div>
                
                <div class="nav">
                    {% if user %}
                    <a href="/dashboard">Dashboard</a>
                    {% if user.role == 'admin' %}
                    <a href="/admin/dashboard">Admin Panel</a>
                    <a href="/users">Manage Users</a>
                    {% endif %}
                    <a href="/auth/logout">Logout</a>
                    {% else %}
                    <a href="/auth/login">Login</a>
                    <a href="/auth/register">Register</a>
                    {% endif %}
                    <a href="/api/v1/users">API Demo</a>
                </div>
                
                <div class="feature">
                    <h3>Key Features</h3>
                    <ul>
                        <li><strong>Zero Dependencies:</strong> No external packages required</li>
                        <li><strong>Async by Default:</strong> Built for modern Python async/await</li>
                        <li><strong>Flask-like Syntax:</strong> Familiar and intuitive API</li>
                        <li><strong>Blueprint Support:</strong> Modular application architecture</li>
                        <li><strong>Template Engine:</strong> Jinja-like templating with improvements</li>
                        <li><strong>Built-in Security:</strong> Session management, CORS, etc.</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>Quick Start</h3>
                    <p>This example demonstrates:</p>
                    <ul>
                        <li>Blueprint patterns for MVC architecture</li>
                        <li>Authentication and authorization</li>
                        <li>RESTful API development</li>
                        <li>Template rendering with context</li>
                        <li>Error handling and middleware</li>
                        <li>Session management</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """, user=user)

    @app.route('/dashboard')
    @require_auth
    async def dashboard(request):
        """User dashboard"""
        user = get_current_user(request)
        
        # Mock user data
        user_stats = {
            'posts_created': 15,
            'comments_made': 42,
            'last_activity': '2 hours ago'
        }
        
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>Dashboard</h1>
            <p>Welcome back, {{ user.email }}!</p>
            
            <h2>Your Statistics</h2>
            <ul>
                <li>Posts Created: {{ stats.posts_created }}</li>
                <li>Comments Made: {{ stats.comments_made }}</li>
                <li>Last Activity: {{ stats.last_activity }}</li>
            </ul>
            
            <h2>Quick Actions</h2>
            <ul>
                <li><a href="/posts">View Posts</a></li>
                <li><a href="/profile">Edit Profile</a></li>
                {% if user.role == 'admin' %}
                <li><a href="/admin/dashboard">Admin Panel</a></li>
                {% endif %}
            </ul>
            
            <p><a href="/">Home</a> | <a href="/auth/logout">Logout</a></p>
        </body>
        </html>
        """, user=user, stats=user_stats)

    @app.route('/api/docs')
    async def api_docs(request):
        """API documentation page"""
        return render_template("""
        <!DOCTYPE html>
        <html>
        <head><title>API Documentation</title></head>
        <body>
            <h1>API Documentation</h1>
            <h2>Endpoints</h2>
            <ul>
                <li><strong>GET /api/v1/users</strong> - List all users</li>
                <li><strong>GET /api/v1/users/{id}</strong> - Get specific user</li>
                <li><strong>POST /api/v1/users</strong> - Create new user</li>
                <li><strong>PUT /api/v1/users/{id}</strong> - Update user</li>
                <li><strong>DELETE /api/v1/users/{id}</strong> - Delete user</li>
            </ul>
            
            <h2>Example Usage</h2>
            <pre>
# List users
curl http://localhost:5000/api/v1/users

# Create user
curl -X POST http://localhost:5000/api/v1/users \\
     -H "Content-Type: application/json" \\
     -d '{"name": "John Doe", "email": "john@example.com"}'
            </pre>
            
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        """)


# ============================================================================
# 5. APPLICATION FACTORY & CONFIGURATION
# ============================================================================

def create_production_app() -> AsyncFlask:
    """Create production application with all features"""
    app = create_app({'debug': False})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # Setup main routes
    setup_main_routes(app)
    
    return app

def create_development_app() -> AsyncFlask:
    """Create development application with debug features"""
    app = create_app({'debug': True})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # Setup main routes
    setup_main_routes(app)
    
    # Development-only routes
    @app.route('/debug/session')
    async def debug_session(request):
        """Debug session information"""
        session_id = request.cookies.get('session_id')
        session_data = request.app.session.get_session(session_id) if session_id else None
        
        return jsonify({
            'session_id': session_id,
            'session_data': session_data,
            'cookies': dict(request.cookies),
            'headers': dict(request.headers)
        })
    
    return app


# ============================================================================
# 6. RUNNING THE APPLICATION
# ============================================================================

if __name__ == '__main__':
    import sys
    
    # Choose environment
    env = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    if env == 'production':
        app = create_production_app()
        print("Starting production server...")
    else:
        app = create_development_app()
        print("Starting development server...")
    
    print("=" * 60)
    print("Soloweb Framework - Complete Example")
    print("=" * 60)
    print("Features demonstrated:")
    print("✅ Blueprint patterns for modular architecture")
    print("✅ Authentication and session management")
    print("✅ Template engine with Jinja-like syntax")
    print("✅ RESTful API development")
    print("✅ Admin panel with role-based access")
    print("✅ Error handling and middleware")
    print("✅ CORS support")
    print("=" * 60)
    print("Available routes:")
    print("  Home: http://localhost:5000/")
    print("  Login: http://localhost:5000/auth/login")
    print("  Dashboard: http://localhost:5000/dashboard")
    print("  Admin: http://localhost:5000/admin/dashboard")
    print("  API: http://localhost:5000/api/v1/users")
    print("  API Docs: http://localhost:5000/api/docs")
    if env == 'development':
        print("  Debug: http://localhost:5000/debug/session")
    print("=" * 60)
    print("Test credentials: admin@example.com / password")
    print("=" * 60)
    
    # Run the application
    app.run(debug=(env == 'development'), host='0.0.0.0', port=5000)


# ============================================================================
# 7. BEST PRACTICES & PATTERNS
# ============================================================================

"""
BEST PRACTICES FOR SOLOWEB FRAMEWORK:

1. APPLICATION STRUCTURE:
   - Use application factory pattern (create_app())
   - Separate configuration for different environments
   - Register blueprints for modular organization
   - Use meaningful URL prefixes for blueprints

2. BLUEPRINT PATTERNS:
   - Group related functionality in blueprints
   - Use blueprint-specific middleware and error handlers
   - Keep blueprints focused and single-purpose
   - Use descriptive blueprint names and URL prefixes

3. TEMPLATE ENGINE:
   - Use templates for HTML generation
   - Leverage filters and functions for data transformation
   - Use conditionals and loops for dynamic content
   - Keep templates clean and readable

4. AUTHENTICATION & AUTHORIZATION:
   - Use session-based authentication
   - Implement role-based access control
   - Use decorators for route protection
   - Validate user permissions in route handlers

5. API DEVELOPMENT:
   - Use consistent URL patterns (/api/v1/resource)
   - Return proper HTTP status codes
   - Use JSON for request/response data
   - Implement proper error handling

6. ERROR HANDLING:
   - Use global error handlers for common errors
   - Provide user-friendly error messages
   - Log errors appropriately
   - Handle both sync and async errors

7. MIDDLEWARE:
   - Use middleware for cross-cutting concerns
   - Add security headers
   - Implement logging and monitoring
   - Handle CORS properly

8. TESTING:
   - Test individual blueprints
   - Test authentication flows
   - Test API endpoints
   - Use mock data for testing

9. SECURITY:
   - Use secure session management
   - Validate and sanitize input
   - Implement proper CSRF protection
   - Use HTTPS in production

10. PERFORMANCE:
    - Use async/await properly
    - Implement caching where appropriate
    - Optimize database queries
    - Use connection pooling

EXAMPLE USAGE:

# Create application
app = create_production_app()

# Add custom middleware
app.add_middleware(YourCustomMiddleware())

# Register additional blueprints
app.register_blueprint(your_custom_bp)

# Run the application
app.run(debug=False, host='0.0.0.0', port=5000)
""" 