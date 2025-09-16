#!/usr/bin/env python3
"""
Test suite for the Soloweb framework
Tests basic functionality, routing, async operations, and blueprints
"""

import asyncio
import json
import time
from soloweb import AsyncWeb, Request, Response, CORSMiddleware, Blueprint


def test_basic_routing():
    """Test basic routing functionality"""
    print("Testing basic routing...")
    
    app = AsyncWeb("test_app")
    
    @app.route('/')
    async def home(request):
        return "Hello, World!"
    
    @app.route('/hello/<name>')
    async def hello_name(request, name):
        return f"Hello, {name}!"
    
    # Test route matching
    route_match = app.router.match_route('GET', '/')
    assert route_match is not None, "Root route should match"
    
    route_match = app.router.match_route('GET', '/hello/Alice')
    assert route_match is not None, "Parameterized route should match"
    handler, params = route_match
    assert params['name'] == 'Alice', "Parameter should be extracted correctly"
    
    print("✅ Basic routing tests passed")


def test_request_parsing():
    """Test request parsing functionality"""
    print("Testing request parsing...")
    
    # Test JSON request
    headers = {'content-type': 'application/json'}
    body = json.dumps({"name": "Alice", "age": 30}).encode()
    request = Request('POST', '/api/users', headers, body)
    
    assert request.json is not None, "JSON should be parsed"
    assert request.json['name'] == 'Alice', "JSON data should be accessible"
    
    # Test form data
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    body = b'name=Alice&age=30'
    request = Request('POST', '/form', headers, body)
    
    assert 'name' in request.form, "Form data should be parsed"
    assert request.form['name'] == ['Alice'], "Form data should be accessible"
    
    # Test query parameters
    request = Request('GET', '/search', {}, b'', 'q=test&page=1')
    assert request.args['q'] == ['test'], "Query parameters should be parsed"
    assert request.args['page'] == ['1'], "Query parameters should be parsed"
    
    print("✅ Request parsing tests passed")


def test_response_handling():
    """Test response handling functionality"""
    print("Testing response handling...")
    
    # Test string response
    response = Response("Hello, World!")
    assert response.status_code == 200, "Default status code should be 200"
    assert response.headers['content-type'] == 'text/html; charset=utf-8', "Content type should be set"
    
    # Test JSON response
    data = {"message": "Hello", "status": "success"}
    response = Response(data)
    assert response.headers['content-type'] == 'application/json', "JSON content type should be set"
    
    # Test custom status code
    response = Response("Not Found", 404)
    assert response.status_code == 404, "Status code should be set correctly"
    
    # Test cookies
    response = Response("Hello")
    response.set_cookie('session_id', 'abc123', max_age=3600)
    assert 'session_id' in response.cookies, "Cookie should be set"
    
    print("✅ Response handling tests passed")


def test_session_management():
    """Test session management functionality"""
    print("Testing session management...")
    
    app = AsyncWeb("test_app", secret_key="test_secret")
    
    # Create session
    session_data = {"user_id": 123, "username": "alice"}
    session_id = app.session.create_session(session_data)
    assert session_id is not None, "Session ID should be generated"
    
    # Retrieve session
    retrieved_data = app.session.get_session(session_id)
    assert retrieved_data is not None, "Session data should be retrievable"
    assert retrieved_data['user_id'] == 123, "Session data should be correct"
    
    # Update session
    app.session.update_session(session_id, {"user_id": 456, "username": "bob"})
    updated_data = app.session.get_session(session_id)
    assert updated_data['user_id'] == 456, "Session should be updated"
    
    # Delete session
    app.session.delete_session(session_id)
    deleted_data = app.session.get_session(session_id)
    assert deleted_data is None, "Session should be deleted"
    
    print("✅ Session management tests passed")


def test_middleware():
    """Test middleware functionality"""
    print("Testing middleware...")
    
    app = AsyncWeb("test_app")
    cors_middleware = CORSMiddleware()
    app.add_middleware(cors_middleware)
    
    # Test CORS preflight request
    headers = {'origin': 'http://localhost:3000'}
    request = Request('OPTIONS', '/api/users', headers, b'')
    
    # This would normally be handled by the full request cycle
    # For now, just test that middleware is added
    assert len(app.middleware) == 1, "Middleware should be added"
    assert isinstance(app.middleware[0], CORSMiddleware), "CORS middleware should be added"
    
    print("✅ Middleware tests passed")


async def test_async_operations():
    """Test async operations"""
    print("Testing async operations...")
    
    app = AsyncWeb("test_app")
    
    @app.route('/async-test')
    async def async_test(request):
        # Simulate async work
        await asyncio.sleep(0.1)
        return "Async response"
    
    # Test that the route handler is async
    route_match = app.router.match_route('GET', '/async-test')
    assert route_match is not None, "Async route should be registered"
    handler, _ = route_match
    assert asyncio.iscoroutinefunction(handler), "Handler should be async"
    
    print("✅ Async operations tests passed")


def test_error_handling():
    """Test error handling functionality"""
    print("Testing error handling...")
    
    app = AsyncWeb("test_app")
    
    @app.errorhandler(404)
    async def not_found(request):
        return Response("Custom 404", 404)
    
    @app.errorhandler(500)
    async def server_error(request):
        return Response("Custom 500", 500)
    
    assert 404 in app.error_handlers, "404 error handler should be registered"
    assert 500 in app.error_handlers, "500 error handler should be registered"
    
    print("✅ Error handling tests passed")


def test_blueprint_basic():
    """Test basic blueprint functionality"""
    print("Testing basic blueprint functionality...")
    
    app = AsyncWeb("test_app")
    
    # Create a blueprint
    auth_bp = Blueprint('auth', url_prefix='/auth')
    
    @auth_bp.route('/login')
    async def login(request):
        return "Login page"
    
    @auth_bp.route('/logout')
    async def logout(request):
        return "Logout page"
    
    # Register blueprint
    app.register_blueprint(auth_bp)
    
    # Test that routes are registered with prefix
    route_match = app.router.match_route('GET', '/auth/login')
    assert route_match is not None, "Blueprint route should be registered with prefix"
    
    route_match = app.router.match_route('GET', '/auth/logout')
    assert route_match is not None, "Blueprint route should be registered with prefix"
    
    # Test that blueprint is stored
    assert 'auth' in app.blueprints, "Blueprint should be stored in app"
    assert app.blueprints['auth'] == auth_bp, "Blueprint should be accessible"
    
    print("✅ Basic blueprint tests passed")


def test_blueprint_mvc():
    """Test blueprint for MVC architecture"""
    print("Testing blueprint MVC architecture...")
    
    app = AsyncWeb("test_app")
    
    # Create user blueprint (Model-View-Controller)
    users_bp = Blueprint('users', url_prefix='/users')
    
    # Controller functions
    @users_bp.route('/')
    async def list_users(request):
        # This would normally fetch from a database
        users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        return Response(users)
    
    @users_bp.route('/<int:user_id>')
    async def get_user(request, user_id):
        # This would normally fetch from a database
        user = {"id": user_id, "name": f"User {user_id}"}
        return Response(user)
    
    @users_bp.route('/', methods=['POST'])
    async def create_user(request):
        # This would normally save to a database
        user_data = request.json
        return Response({"message": "User created", "user": user_data}, 201)
    
    # Register blueprint
    app.register_blueprint(users_bp)
    
    # Test MVC routes
    route_match = app.router.match_route('GET', '/users/')
    assert route_match is not None, "List users route should be registered"
    
    route_match = app.router.match_route('GET', '/users/123')
    assert route_match is not None, "Get user route should be registered"
    handler, params = route_match
    assert params['user_id'] == '123', "User ID parameter should be extracted"
    
    route_match = app.router.match_route('POST', '/users/')
    assert route_match is not None, "Create user route should be registered"
    
    print("✅ Blueprint MVC tests passed")


def test_blueprint_hooks():
    """Test blueprint before/after request hooks"""
    print("Testing blueprint hooks...")
    
    app = AsyncWeb("test_app")
    
    # Create blueprint with hooks
    api_bp = Blueprint('api', url_prefix='/api')
    
    @api_bp.before_request
    async def before_api_request():
        # This would normally do authentication, logging, etc.
        pass
    
    @api_bp.after_request
    async def after_api_request(response):
        # This would normally add headers, logging, etc.
        response.headers['X-API-Version'] = '1.0'
        return response
    
    @api_bp.route('/data')
    async def get_data(request):
        return {"data": "test"}
    
    # Register blueprint
    app.register_blueprint(api_bp)
    
    # Test that hooks are registered
    assert len(app.before_request_handlers) == 1, "Blueprint before_request should be registered"
    assert len(app.after_request_handlers) == 1, "Blueprint after_request should be registered"
    
    print("✅ Blueprint hooks tests passed")


def test_blueprint_error_handlers():
    """Test blueprint error handlers"""
    print("Testing blueprint error handlers...")
    
    app = AsyncWeb("test_app")
    
    # Create blueprint with error handlers
    admin_bp = Blueprint('admin', url_prefix='/admin')
    
    @admin_bp.errorhandler(403)
    async def forbidden(request):
        return Response("Access denied", 403)
    
    @admin_bp.route('/dashboard')
    async def dashboard(request):
        return "Admin dashboard"
    
    # Register blueprint
    app.register_blueprint(admin_bp)
    
    # Test that error handlers are registered
    assert 403 in app.error_handlers, "Blueprint error handler should be registered"
    
    print("✅ Blueprint error handlers tests passed")


def test_blueprint_url_for():
    """Test blueprint URL generation"""
    print("Testing blueprint URL generation...")
    
    app = AsyncWeb("test_app")
    
    # Create blueprint
    blog_bp = Blueprint('blog', url_prefix='/blog')
    
    @blog_bp.route('/posts/<int:post_id>')
    async def get_post(request, post_id):
        return f"Post {post_id}"
    
    # Register blueprint
    app.register_blueprint(blog_bp)
    
    # Test URL generation
    url = app.url_for('blog.get_post', post_id=123)
    assert url == '/blog/posts/123', "Blueprint URL should be generated correctly"
    
    # Test blueprint internal URL generation
    url = blog_bp.url_for('get_post', post_id=456)
    assert url == '/blog/posts/456', "Blueprint internal URL should be generated correctly"
    
    print("✅ Blueprint URL generation tests passed")


def test_multiple_blueprints():
    """Test multiple blueprints working together"""
    print("Testing multiple blueprints...")
    
    app = AsyncWeb("test_app")
    
    # Create multiple blueprints
    auth_bp = Blueprint('auth', url_prefix='/auth')
    users_bp = Blueprint('users', url_prefix='/users')
    admin_bp = Blueprint('admin', url_prefix='/admin')
    
    @auth_bp.route('/login')
    async def login(request):
        return "Login"
    
    @users_bp.route('/profile')
    async def profile(request):
        return "Profile"
    
    @admin_bp.route('/dashboard')
    async def dashboard(request):
        return "Dashboard"
    
    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    
    # Test all routes are registered
    assert app.router.match_route('GET', '/auth/login') is not None, "Auth route should be registered"
    assert app.router.match_route('GET', '/users/profile') is not None, "Users route should be registered"
    assert app.router.match_route('GET', '/admin/dashboard') is not None, "Admin route should be registered"
    
    # Test blueprint count
    assert len(app.blueprints) == 3, "All blueprints should be registered"
    
    print("✅ Multiple blueprints tests passed")


def test_blueprint_duplicate_registration():
    """Test that duplicate blueprint registration fails"""
    print("Testing duplicate blueprint registration...")
    
    app = AsyncWeb("test_app")
    
    # Create blueprint
    bp1 = Blueprint('test', url_prefix='/test')
    bp2 = Blueprint('test', url_prefix='/test2')
    
    # Register first blueprint
    app.register_blueprint(bp1)
    
    # Try to register duplicate blueprint
    try:
        app.register_blueprint(bp2)
        assert False, "Duplicate blueprint registration should fail"
    except ValueError:
        # Expected behavior
        pass
    
    print("✅ Duplicate blueprint registration tests passed")


def run_all_tests():
    """Run all tests"""
    print("Running Soloweb Framework Tests")
    print("=" * 50)
    
    try:
        test_basic_routing()
        test_request_parsing()
        test_response_handling()
        test_session_management()
        test_middleware()
        asyncio.run(test_async_operations())
        test_error_handling()
        
        # Blueprint tests
        test_blueprint_basic()
        test_blueprint_mvc()
        test_blueprint_hooks()
        test_blueprint_error_handlers()
        test_blueprint_url_for()
        test_multiple_blueprints()
        test_blueprint_duplicate_registration()
        
        print("=" * 50)
        print("🎉 All tests passed! The framework with blueprints is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests() 