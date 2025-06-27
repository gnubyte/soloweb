#!/usr/bin/env python3
"""
Template Engine Example

This example demonstrates the Soloweb template engine with various features:
- Variable interpolation
- Filters and functions
- Conditionals and loops
- Nested data structures
- Real-world use cases
"""

from soloweb import AsyncFlask, render_template

app = AsyncFlask("template_example")


@app.route('/')
async def home(request):
    """Home page with template rendering"""
    context = {
        'title': 'Welcome to Soloweb',
        'user': {
            'name': 'Alice Smith',
            'role': 'admin',
            'is_admin': True
        },
        'posts': [
            {
                'title': 'Getting Started with Soloweb',
                'author': 'Alice Smith',
                'date': '2024-01-15',
                'content': 'Soloweb is a powerful async web framework with zero external dependencies.',
                'tags': ['Python', 'Web Development', 'Async']
            },
            {
                'title': 'Template Engine Features',
                'author': 'Bob Johnson',
                'date': '2024-01-10',
                'content': 'Learn about the Jinja-like template engine with improvements.',
                'tags': ['Templates', 'Jinja', 'Features']
            }
        ],
        'stats': {
            'total_users': 1250,
            'total_posts': 89,
            'active_users': 342
        }
    }
    
    html = render_template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            nav { margin-top: 10px; }
            nav a { color: #ecf0f1; text-decoration: none; margin-right: 15px; }
            nav a:hover { color: #3498db; }
            .user-info { background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: #3498db; color: white; padding: 20px; border-radius: 5px; text-align: center; }
            .posts { margin-top: 20px; }
            .post { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
            .post h3 { margin-top: 0; color: #2c3e50; }
            .meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; }
            .tags { margin-top: 10px; }
            .tag { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }
            footer { margin-top: 30px; text-align: center; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{{ title | upper }}</h1>
                {% if user %}
                <nav>
                    <span>Welcome, {{ user.name | title }}!</span>
                    {% if user.is_admin %}
                    <a href="/admin">Admin Panel</a>
                    {% endif %}
                    <a href="/profile">Profile</a>
                    <a href="/logout">Logout</a>
                </nav>
                {% else %}
                <nav>
                    <a href="/login">Login</a>
                    <a href="/register">Register</a>
                </nav>
                {% endif %}
            </header>
            
            {% if user %}
            <div class="user-info">
                <h3>User Information</h3>
                <p><strong>Name:</strong> {{ user.name | title }}</p>
                <p><strong>Role:</strong> {{ user.role | upper }}</p>
                {% if user.is_admin %}
                <p><strong>Status:</strong> <span style="color: #e74c3c;">Administrator</span></p>
                {% else %}
                <p><strong>Status:</strong> <span style="color: #27ae60;">Regular User</span></p>
                {% endif %}
            </div>
            {% endif %}
            
            <div class="stats">
                <div class="stat-card">
                    <h3>{{ stats.total_users | default(0) }}</h3>
                    <p>Total Users</p>
                </div>
                <div class="stat-card">
                    <h3>{{ stats.total_posts | default(0) }}</h3>
                    <p>Total Posts</p>
                </div>
                <div class="stat-card">
                    <h3>{{ stats.active_users | default(0) }}</h3>
                    <p>Active Users</p>
                </div>
            </div>
            
            <div class="posts">
                <h2>Recent Posts ({{ posts | length }})</h2>
                {% if posts %}
                    {% for post in posts %}
                    <div class="post">
                        <h3>{{ post.title | title }}</h3>
                        <div class="meta">
                            By {{ post.author }} on {{ post.date }}
                        </div>
                        <p>{{ post.content | truncate(150) }}</p>
                        {% if post.tags %}
                        <div class="tags">
                            {% for tag in post.tags %}
                            <span class="tag">{{ tag | lower }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No posts available.</p>
                {% endif %}
            </div>
            
            <footer>
                <p>&copy; 2024 {{ title }}. Built with Soloweb Framework.</p>
            </footer>
        </div>
    </body>
    </html>
    """, **context)
    
    return html


@app.route('/demo')
async def demo(request):
    """Demo page showing template features"""
    context = {
        'numbers': list(range(1, 11)),
        'fruits': ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'],
        'users': [
            {'name': 'Alice', 'age': 25, 'role': 'admin'},
            {'name': 'Bob', 'age': 30, 'role': 'user'},
            {'name': 'Charlie', 'age': 35, 'role': 'moderator'}
        ],
        'show_admin': True,
        'message': 'Hello, World!'
    }
    
    html = render_template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Template Engine Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .demo-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .demo-section h3 { margin-top: 0; color: #2c3e50; }
            .code { background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }
            .result { background: #e8f5e8; padding: 10px; border-radius: 3px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Soloweb Template Engine Demo</h1>
        
        <div class="demo-section">
            <h3>1. Basic Variables</h3>
            <div class="code">Message: {{ message }}</div>
            <div class="result">Message: {{ message }}</div>
        </div>
        
        <div class="demo-section">
            <h3>2. Filters</h3>
            <div class="code">Original: {{ message }}<br>
            Upper: {{ message | upper }}<br>
            Lower: {{ message | lower }}<br>
            Title: {{ message | title }}</div>
            <div class="result">
                Original: {{ message }}<br>
                Upper: {{ message | upper }}<br>
                Lower: {{ message | lower }}<br>
                Title: {{ message | title }}
            </div>
        </div>
        
        <div class="demo-section">
            <h3>3. Functions</h3>
            <div class="code">Numbers: {{ numbers | join(', ') }}<br>
            Count: {{ numbers | length }}<br>
            Max: {{ max(numbers) }}<br>
            Min: {{ min(numbers) }}<br>
            Sum: {{ sum(numbers) }}</div>
            <div class="result">
                Numbers: {{ numbers | join(', ') }}<br>
                Count: {{ numbers | length }}<br>
                Max: {{ max(numbers) }}<br>
                Min: {{ min(numbers) }}<br>
                Sum: {{ sum(numbers) }}
            </div>
        </div>
        
        <div class="demo-section">
            <h3>4. Conditionals</h3>
            <div class="code">
            {% if show_admin %}
            <p>Admin panel is visible</p>
            {% else %}
            <p>Admin panel is hidden</p>
            {% endif %}
            </div>
            <div class="result">
            {% if show_admin %}
            <p>Admin panel is visible</p>
            {% else %}
            <p>Admin panel is hidden</p>
            {% endif %}
            </div>
        </div>
        
        <div class="demo-section">
            <h3>5. Loops</h3>
            <div class="code">
            <h4>Fruits:</h4>
            <ul>
            {% for fruit in fruits %}
                <li>{{ fruit | lower }}</li>
            {% endfor %}
            </ul>
            </div>
            <div class="result">
            <h4>Fruits:</h4>
            <ul>
            {% for fruit in fruits %}
                <li>{{ fruit | lower }}</li>
            {% endfor %}
            </ul>
            </div>
        </div>
        
        <div class="demo-section">
            <h3>6. Nested Data</h3>
            <div class="code">
            <h4>Users:</h4>
            {% for user in users %}
            <div>
                <strong>{{ user.name | title }}</strong> ({{ user.age }} years old) - {{ user.role | upper }}
            </div>
            {% endfor %}
            </div>
            <div class="result">
            <h4>Users:</h4>
            {% for user in users %}
            <div>
                <strong>{{ user.name | title }}</strong> ({{ user.age }} years old) - {{ user.role | upper }}
            </div>
            {% endfor %}
            </div>
        </div>
        
        <div class="demo-section">
            <h3>7. Complex Example</h3>
            <div class="code">
            {% for user in users %}
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
                <h4>{{ user.name | title }}</h4>
                <p>Age: {{ user.age }}</p>
                <p>Role: {{ user.role | upper }}</p>
                {% if user.role == 'admin' %}
                <p style="color: red;">This user has admin privileges</p>
                {% elif user.role == 'moderator' %}
                <p style="color: orange;">This user has moderator privileges</p>
                {% else %}
                <p style="color: green;">This user has regular privileges</p>
                {% endif %}
            </div>
            {% endfor %}
            </div>
            <div class="result">
            {% for user in users %}
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
                <h4>{{ user.name | title }}</h4>
                <p>Age: {{ user.age }}</p>
                <p>Role: {{ user.role | upper }}</p>
                {% if user.role == 'admin' %}
                <p style="color: red;">This user has admin privileges</p>
                {% elif user.role == 'moderator' %}
                <p style="color: orange;">This user has moderator privileges</p>
                {% else %}
                <p style="color: green;">This user has regular privileges</p>
                {% endif %}
            </div>
            {% endfor %}
            </div>
        </div>
        
        <p><a href="/">Back to Home</a></p>
    </body>
    </html>
    """, **context)
    
    return html


if __name__ == '__main__':
    print("Starting Template Engine Example Server...")
    print("Visit http://localhost:5000 for the main example")
    print("Visit http://localhost:5000/demo for the feature demo")
    app.run(debug=True) 