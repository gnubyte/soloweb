#!/usr/bin/env python3
"""
Example Soloweb application demonstrating MVC architecture with blueprints

This example shows how to organize a web application using:
- Blueprints for modular organization
- Model-View-Controller pattern
- Multiple blueprints working together
- Authentication and authorization
- API and web interfaces
"""

import asyncio
from soloweb import AsyncWeb, Blueprint, Response, Request


# ============================================================================
# MODELS (Data Layer)
# ============================================================================

class User:
    """Simple user model"""
    def __init__(self, id: int, username: str, email: str, role: str = "user"):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

class Post:
    """Simple post model"""
    def __init__(self, id: int, title: str, content: str, author_id: int):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id

# In-memory storage (in a real app, this would be a database)
users_db = {
    1: User(1, "alice", "alice@example.com", "admin"),
    2: User(2, "bob", "bob@example.com", "user"),
    3: User(3, "charlie", "charlie@example.com", "user")
}

posts_db = {
    1: Post(1, "Hello World", "This is my first post!", 1),
    2: Post(2, "Async Programming", "Async programming is awesome!", 2),
    3: Post(3, "Web Frameworks", "Soloweb is a great framework!", 1)
}


# ============================================================================
# AUTHENTICATION BLUEPRINT (Controller)
# ============================================================================

auth_bp = Blueprint('auth', url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
async def login(request: Request):
    """Login controller"""
    if request.method == 'GET':
        # View: Return login form
        return """
        <h1>Login</h1>
        <form method="POST">
            <label>Username: <input name="username" required></label><br>
            <label>Password: <input name="password" type="password" required></label><br>
            <button type="submit">Login</button>
        </form>
        """
    
    elif request.method == 'POST':
        # Controller: Handle login logic
        username = request.form.get('username', [''])[0]
        password = request.form.get('password', [''])[0]
        
        # Simple authentication (in real app, check against database)
        if username == "admin" and password == "password":
            # Create session
            session_data = {"user_id": 1, "username": username, "role": "admin"}
            session_id = request.app.session.create_session(session_data)
            
            response = Response("Login successful! <a href='/dashboard'>Go to Dashboard</a>")
            response.set_cookie('session_id', session_id, max_age=3600)
            return response
        else:
            return Response("Invalid credentials", 401)

@auth_bp.route('/logout')
async def logout(request: Request):
    """Logout controller"""
    session_id = request.cookies.get('session_id')
    if session_id:
        request.app.session.delete_session(session_id)
    
    response = Response("Logged out successfully! <a href='/auth/login'>Login again</a>")
    response.set_cookie('session_id', '', max_age=0)
    return response


# ============================================================================
# USERS BLUEPRINT (MVC for User Management)
# ============================================================================

users_bp = Blueprint('users', url_prefix='/users')

@users_bp.route('/')
async def list_users(request: Request):
    """List all users (Controller)"""
    # Model: Get data
    users = list(users_db.values())
    
    # View: Format response
    user_list = "\n".join([
        f"<li><a href='/users/{user.id}'>{user.username}</a> ({user.role})</li>"
        for user in users
    ])
    
    return f"""
    <h1>Users</h1>
    <ul>{user_list}</ul>
    <p><a href='/'>Back to Home</a></p>
    """

@users_bp.route('/<int:user_id>')
async def get_user(request: Request, user_id: int):
    """Get specific user (Controller)"""
    # Model: Get data
    user = users_db.get(user_id)
    if not user:
        return Response("User not found", 404)
    
    # View: Format response
    return f"""
    <h1>User Profile</h1>
    <p><strong>ID:</strong> {user.id}</p>
    <p><strong>Username:</strong> {user.username}</p>
    <p><strong>Email:</strong> {user.email}</p>
    <p><strong>Role:</strong> {user.role}</p>
    <p><a href='/users/'>Back to Users</a></p>
    """

@users_bp.route('/', methods=['POST'])
async def create_user(request: Request):
    """Create new user (Controller)"""
    # Model: Create user
    user_data = request.json or {}
    new_id = max(users_db.keys()) + 1
    
    new_user = User(
        id=new_id,
        username=user_data.get('username', f'user{new_id}'),
        email=user_data.get('email', f'user{new_id}@example.com'),
        role=user_data.get('role', 'user')
    )
    
    users_db[new_id] = new_user
    
    # View: Return response
    return Response({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }
    }, 201)


# ============================================================================
# POSTS BLUEPRINT (MVC for Blog Posts)
# ============================================================================

posts_bp = Blueprint('posts', url_prefix='/posts')

@posts_bp.route('/')
async def list_posts(request: Request):
    """List all posts (Controller)"""
    # Model: Get data
    posts = list(posts_db.values())
    
    # View: Format response
    post_list = "\n".join([
        f"<li><a href='/posts/{post.id}'>{post.title}</a> by User {post.author_id}</li>"
        for post in posts
    ])
    
    return f"""
    <h1>Blog Posts</h1>
    <ul>{post_list}</ul>
    <p><a href='/'>Back to Home</a></p>
    """

@posts_bp.route('/<int:post_id>')
async def get_post(request: Request, post_id: int):
    """Get specific post (Controller)"""
    # Model: Get data
    post = posts_db.get(post_id)
    if not post:
        return Response("Post not found", 404)
    
    author = users_db.get(post.author_id)
    author_name = author.username if author else "Unknown"
    
    # View: Format response
    return f"""
    <h1>{post.title}</h1>
    <p><em>By {author_name}</em></p>
    <div>{post.content}</div>
    <p><a href='/posts/'>Back to Posts</a></p>
    """

@posts_bp.route('/', methods=['POST'])
async def create_post(request: Request):
    """Create new post (Controller)"""
    # Check authentication
    session_id = request.cookies.get('session_id')
    if not session_id:
        return Response("Authentication required", 401)
    
    session_data = request.app.session.get_session(session_id)
    if not session_data:
        return Response("Invalid session", 401)
    
    # Model: Create post
    post_data = request.json or {}
    new_id = max(posts_db.keys()) + 1
    
    new_post = Post(
        id=new_id,
        title=post_data.get('title', f'Post {new_id}'),
        content=post_data.get('content', 'No content'),
        author_id=session_data['user_id']
    )
    
    posts_db[new_id] = new_post
    
    # View: Return response
    return Response({
        "message": "Post created successfully",
        "post": {
            "id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "author_id": new_post.author_id
        }
    }, 201)


# ============================================================================
# ADMIN BLUEPRINT (Admin Interface)
# ============================================================================

admin_bp = Blueprint('admin', url_prefix='/admin')

@admin_bp.before_request
async def require_admin():
    """Middleware to require admin access"""
    # This would be implemented in the full request cycle
    pass

@admin_bp.route('/dashboard')
async def admin_dashboard(request: Request):
    """Admin dashboard (Controller)"""
    # Check authentication
    session_id = request.cookies.get('session_id')
    if not session_id:
        return Response("Authentication required", 401)
    
    session_data = request.app.session.get_session(session_id)
    if not session_data or session_data.get('role') != 'admin':
        return Response("Admin access required", 403)
    
    # Model: Get admin data
    total_users = len(users_db)
    total_posts = len(posts_db)
    
    # View: Format response
    return f"""
    <h1>Admin Dashboard</h1>
    <p>Welcome, {session_data['username']}!</p>
    <div>
        <h2>Statistics</h2>
        <p>Total Users: {total_users}</p>
        <p>Total Posts: {total_posts}</p>
    </div>
    <div>
        <h2>Quick Actions</h2>
        <ul>
            <li><a href='/users/'>Manage Users</a></li>
            <li><a href='/posts/'>Manage Posts</a></li>
            <li><a href='/auth/logout'>Logout</a></li>
        </ul>
    </div>
    """


# ============================================================================
# API BLUEPRINT (REST API)
# ============================================================================

api_bp = Blueprint('api', url_prefix='/api/v1')

@api_bp.after_request
async def add_api_headers(response: Response):
    """Add API headers to all API responses"""
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-API-Version'] = '1.0'
    return response

@api_bp.route('/users')
async def api_list_users(request: Request):
    """API endpoint to list users"""
    users = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        for user in users_db.values()
    ]
    return Response(users)

@api_bp.route('/users/<int:user_id>')
async def api_get_user(request: Request, user_id: int):
    """API endpoint to get specific user"""
    user = users_db.get(user_id)
    if not user:
        return Response({"error": "User not found"}, 404)
    
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })

@api_bp.route('/posts')
async def api_list_posts(request: Request):
    """API endpoint to list posts"""
    posts = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id
        }
        for post in posts_db.values()
    ]
    return Response(posts)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

app = AsyncWeb(__name__, secret_key="your-secret-key-here")

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

@app.route('/')
async def home(request: Request):
    """Home page"""
    return """
    <h1>Welcome to Soloweb MVC Example</h1>
    <p>This example demonstrates Model-View-Controller architecture using blueprints.</p>
    
    <h2>Available Modules:</h2>
    <ul>
        <li><a href='/auth/login'>Authentication</a> - Login/logout functionality</li>
        <li><a href='/users/'>User Management</a> - CRUD operations for users</li>
        <li><a href='/posts/'>Blog Posts</a> - CRUD operations for posts</li>
        <li><a href='/admin/dashboard'>Admin Panel</a> - Administrative interface</li>
        <li><a href='/api/v1/users'>API</a> - REST API endpoints</li>
    </ul>
    
    <h2>Test Credentials:</h2>
    <p>Username: admin, Password: password</p>
    """

@app.errorhandler(404)
async def not_found(request: Request):
    """Custom 404 handler"""
    return Response("""
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href='/'>Go back home</a></p>
    """, 404)

@app.errorhandler(500)
async def server_error(request: Request):
    """Custom 500 handler"""
    return Response("""
    <h1>Internal Server Error</h1>
    <p>Something went wrong on our end.</p>
    <p><a href='/'>Go back home</a></p>
    """, 500)


if __name__ == '__main__':
    print("Starting Soloweb MVC Example Application...")
    print("Visit http://127.0.0.1:5000 to see the application")
    print("Test login: admin / password")
    app.run(host='127.0.0.1', port=5000, debug=True) 