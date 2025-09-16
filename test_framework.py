#!/usr/bin/env python3
"""
Test suite for the Soloweb framework
Tests basic functionality, routing, and async operations
"""

import asyncio
import json
import time
from soloweb import AsyncWeb, Request, Response, CORSMiddleware


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


def run_all_tests():
    """Run all tests"""
    print("Running Soloweb Framework Tests")
    print("=" * 40)
    
    try:
        test_basic_routing()
        test_request_parsing()
        test_response_handling()
        test_session_management()
        test_middleware()
        asyncio.run(test_async_operations())
        test_error_handling()
        
        print("=" * 40)
        print("🎉 All tests passed! The framework is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests() 