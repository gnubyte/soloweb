#!/usr/bin/env python3
"""
Test suite for the Soloweb Template Engine
Tests all template features including variables, filters, functions, conditionals, and loops
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soloweb.templates import Template, render_template, TemplateError


def test_basic_variables():
    """Test basic variable interpolation"""
    print("Testing basic variables...")
    
    template = "Hello, {{ name }}!"
    result = render_template(template, name="World")
    assert result == "Hello, World!", f"Expected 'Hello, World!', got '{result}'"
    
    # Test with missing variable
    result = render_template(template, other="World")
    assert result == "Hello, !", f"Expected 'Hello, !', got '{result}'"
    
    print("✅ Basic variables tests passed")


def test_nested_variables():
    """Test nested variable access using dot notation"""
    print("Testing nested variables...")
    
    template = "Hello, {{ user.name }}! You are {{ user.role }}."
    context = {
        "user": {
            "name": "Alice",
            "role": "admin"
        }
    }
    result = render_template(template, **context)
    assert result == "Hello, Alice! You are admin.", f"Expected 'Hello, Alice! You are admin.', got '{result}'"
    
    # Test with missing nested key
    template = "Hello, {{ user.name }}! Age: {{ user.age }}."
    result = render_template(template, **context)
    assert result == "Hello, Alice! Age: .", f"Expected 'Hello, Alice! Age: .', got '{result}'"
    
    print("✅ Nested variables tests passed")


def test_filters():
    """Test template filters"""
    print("Testing filters...")
    
    # Basic filters
    template = "{{ text | upper }}"
    result = render_template(template, text="hello world")
    assert result == "HELLO WORLD", f"Expected 'HELLO WORLD', got '{result}'"
    
    template = "{{ text | lower }}"
    result = render_template(template, text="HELLO WORLD")
    assert result == "hello world", f"Expected 'hello world', got '{result}'"
    
    template = "{{ text | title }}"
    result = render_template(template, text="hello world")
    assert result == "Hello World", f"Expected 'Hello World', got '{result}'"
    
    # Filter with arguments
    template = "{{ text | truncate(5) }}"
    result = render_template(template, text="Hello World")
    assert result == "Hello...", f"Expected 'Hello...', got '{result}'"
    
    template = "{{ text | replace('o', '0') }}"
    result = render_template(template, text="Hello World")
    assert result == "Hell0 W0rld", f"Expected 'Hell0 W0rld', got '{result}'"
    
    # Multiple filters
    template = "{{ text | upper | replace('O', '0') }}"
    result = render_template(template, text="hello world")
    assert result == "HELL0 W0RLD", f"Expected 'HELL0 W0RLD', got '{result}'"
    
    # Default filter
    template = "{{ name | default('Anonymous') }}"
    result = render_template(template, name="")
    assert result == "Anonymous", f"Expected 'Anonymous', got '{result}'"
    
    print("✅ Filters tests passed")


def test_functions():
    """Test template functions"""
    print("Testing functions...")
    
    # Basic functions
    template = "{{ len(items) }}"
    result = render_template(template, items=[1, 2, 3, 4, 5])
    assert result == "5", f"Expected '5', got '{result}'"
    
    template = "{{ range(5) | list | join(', ') }}"
    result = render_template(template)
    assert result == "0, 1, 2, 3, 4", f"Expected '0, 1, 2, 3, 4', got '{result}'"
    
    template = "{{ max(numbers) }}"
    result = render_template(template, numbers=[1, 5, 3, 9, 2])
    assert result == "9", f"Expected '9', got '{result}'"
    
    template = "{{ min(numbers) }}"
    result = render_template(template, numbers=[1, 5, 3, 9, 2])
    assert result == "1", f"Expected '1', got '{result}'"
    
    template = "{{ sum(numbers) }}"
    result = render_template(template, numbers=[1, 2, 3, 4, 5])
    assert result == "15", f"Expected '15', got '{result}'"
    
    print("✅ Functions tests passed")


def test_conditionals():
    """Test if/else conditionals"""
    print("Testing conditionals...")
    
    # Basic if
    template = """
    {% if user %}
    Hello, {{ user }}!
    {% endif %}
    """
    result = render_template(template, user="Alice")
    assert "Hello, Alice!" in result, f"Expected 'Hello, Alice!' in result, got '{result}'"
    
    # If with else
    template = """
    {% if user %}
    Hello, {{ user }}!
    {% else %}
    Hello, Anonymous!
    {% endif %}
    """
    result = render_template(template, user="")
    assert "Hello, Anonymous!" in result, f"Expected 'Hello, Anonymous!' in result, got '{result}'"
    
    # Comparisons
    template = """
    {% if age >= 18 %}
    You are an adult.
    {% else %}
    You are a minor.
    {% endif %}
    """
    result = render_template(template, age=20)
    assert "You are an adult." in result, f"Expected 'You are an adult.' in result, got '{result}'"
    
    result = render_template(template, age=16)
    assert "You are a minor." in result, f"Expected 'You are a minor.' in result, got '{result}'"
    
    # Boolean values
    template = """
    {% if is_admin %}
    Welcome, Administrator!
    {% else %}
    Welcome, User!
    {% endif %}
    """
    result = render_template(template, is_admin=True)
    assert "Welcome, Administrator!" in result, f"Expected 'Welcome, Administrator!' in result, got '{result}'"
    
    result = render_template(template, is_admin=False)
    assert "Welcome, User!" in result, f"Expected 'Welcome, User!' in result, got '{result}'"
    
    print("✅ Conditionals tests passed")


def test_loops():
    """Test for loops"""
    print("Testing loops...")
    
    # Basic loop
    template = """
    <ul>
    {% for item in items %}
    <li>{{ item }}</li>
    {% endfor %}
    </ul>
    """
    result = render_template(template, items=["Apple", "Banana", "Cherry"])
    assert "<li>Apple</li>" in result, f"Expected '<li>Apple</li>' in result, got '{result}'"
    assert "<li>Banana</li>" in result, f"Expected '<li>Banana</li>' in result, got '{result}'"
    assert "<li>Cherry</li>" in result, f"Expected '<li>Cherry</li>' in result, got '{result}'"
    
    # Loop with empty list
    result = render_template(template, items=[])
    assert "<li>" not in result, f"Expected no list items, got '{result}'"
    
    # Loop with nested data
    template = """
    {% for user in users %}
    <div class="user">
        <h3>{{ user.name }}</h3>
        <p>Role: {{ user.role }}</p>
    </div>
    {% endfor %}
    """
    users = [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "user"}
    ]
    result = render_template(template, users=users)
    assert "Alice" in result and "admin" in result, f"Expected Alice and admin in result, got '{result}'"
    assert "Bob" in result and "user" in result, f"Expected Bob and user in result, got '{result}'"
    
    print("✅ Loops tests passed")


def test_nested_structures():
    """Test nested if statements and loops"""
    print("Testing nested structures...")
    
    template = """
    {% for user in users %}
    <div class="user">
        <h3>{{ user.name }}</h3>
        {% if user.is_admin %}
        <p class="admin">Administrator</p>
        {% else %}
        <p class="user">Regular User</p>
        {% endif %}
        {% if user.permissions %}
        <ul>
            {% for permission in user.permissions %}
            <li>{{ permission }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    {% endfor %}
    """
    
    users = [
        {
            "name": "Alice",
            "is_admin": True,
            "permissions": ["read", "write", "delete"]
        },
        {
            "name": "Bob",
            "is_admin": False,
            "permissions": ["read"]
        }
    ]
    
    result = render_template(template, users=users)
    assert "Alice" in result and "Administrator" in result, f"Expected Alice and Administrator in result"
    assert "Bob" in result and "Regular User" in result, f"Expected Bob and Regular User in result"
    assert "read" in result and "write" in result and "delete" in result, f"Expected permissions in result"
    
    print("✅ Nested structures tests passed")


def test_error_handling():
    """Test template error handling"""
    print("Testing error handling...")
    
    # Invalid filter
    try:
        template = "{{ text | invalid_filter }}"
        render_template(template, text="hello")
        assert False, "Expected TemplateError for invalid filter"
    except TemplateError:
        pass  # Expected
    
    # Invalid function
    try:
        template = "{{ invalid_function() }}"
        render_template(template)
        assert False, "Expected TemplateError for invalid function"
    except TemplateError:
        pass  # Expected
    
    # Invalid for loop syntax
    try:
        template = "{% for item %}{{ item }}{% endfor %}"
        render_template(template, items=[1, 2, 3])
        assert False, "Expected TemplateError for invalid for loop"
    except TemplateError:
        pass  # Expected
    
    print("✅ Error handling tests passed")


def test_complex_example():
    """Test a complex real-world example"""
    print("Testing complex example...")
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ page_title | default('My Website') }}</title>
    </head>
    <body>
        <header>
            <h1>{{ site_name | upper }}</h1>
            {% if user %}
            <nav>
                <span>Welcome, {{ user.name | title }}!</span>
                {% if user.is_admin %}
                <a href="/admin">Admin Panel</a>
                {% endif %}
                <a href="/logout">Logout</a>
            </nav>
            {% else %}
            <nav>
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            </nav>
            {% endif %}
        </header>
        
        <main>
            {% if posts %}
            <section class="posts">
                <h2>Recent Posts ({{ posts | length }})</h2>
                {% for post in posts %}
                <article>
                    <h3>{{ post.title | title }}</h3>
                    <p class="meta">By {{ post.author }} on {{ post.date }}</p>
                    <p>{{ post.content | truncate(100) }}</p>
                    {% if post.tags %}
                    <div class="tags">
                        {% for tag in post.tags %}
                        <span class="tag">{{ tag | lower }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </article>
                {% endfor %}
            </section>
            {% else %}
            <p>No posts available.</p>
            {% endif %}
        </main>
        
        <footer>
            <p>&copy; {{ current_year }} {{ site_name }}. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """
    
    context = {
        "site_name": "My Blog",
        "page_title": "Home",
        "user": {
            "name": "alice smith",
            "is_admin": True
        },
        "posts": [
            {
                "title": "getting started with python",
                "author": "Alice Smith",
                "date": "2024-01-15",
                "content": "Python is a powerful programming language that's great for beginners and experts alike. In this post, we'll explore the basics of Python programming.",
                "tags": ["Python", "Programming", "Tutorial"]
            },
            {
                "title": "web development tips",
                "author": "Bob Johnson",
                "date": "2024-01-10",
                "content": "Here are some essential tips for modern web development that will help you build better applications.",
                "tags": ["Web Development", "Tips"]
            }
        ],
        "current_year": 2024
    }
    
    result = render_template(template, **context)
    
    # Check key elements
    assert "MY BLOG" in result, "Site name should be uppercase"
    assert "Alice Smith" in result, "User name should be title case"
    assert "Admin Panel" in result, "Admin link should be present"
    assert "Recent Posts (2)" in result, "Should show correct post count"
    assert "Getting Started With Python" in result, "Post title should be title case"
    assert "python" in result.lower(), "Tags should be lowercase"
    assert "2024" in result, "Current year should be present"
    
    print("✅ Complex example test passed")


def run_all_tests():
    """Run all template tests"""
    print("Running Soloweb Template Engine Tests")
    print("=" * 50)
    
    try:
        test_basic_variables()
        test_nested_variables()
        test_filters()
        test_functions()
        test_conditionals()
        test_loops()
        test_nested_structures()
        test_error_handling()
        test_complex_example()
        
        print("=" * 50)
        print("🎉 All template tests passed! The template engine is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests() 