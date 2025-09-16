#!/bin/bash

# Script to build and upload Soloweb package to GitHub releases
# Requires GitHub CLI (gh) to be installed and authenticated

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first:"
    echo "  macOS: brew install gh"
    echo "  Ubuntu: sudo apt install gh"
    echo "  Or visit: https://cli.github.com/"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    print_error "GitHub CLI is not authenticated. Please run: gh auth login"
    exit 1
fi

# Get current version
VERSION=$(grep "__version__" soloweb/__init__.py | cut -d'"' -f2)
print_status "Current version: $VERSION"

# Get repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
print_status "Repository: $REPO"

# Check if release already exists
if gh release view "v$VERSION" &> /dev/null; then
    print_warning "Release v$VERSION already exists!"
    read -p "Do you want to continue and update assets? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Aborted."
        exit 0
    fi
fi

# Build package
print_status "Building package..."
rm -rf build/ dist/ *.egg-info/
python3 setup.py sdist bdist_wheel

# Check what was created
DIST_FILES=$(ls dist/)
print_success "Created distribution files: $DIST_FILES"

# Create release (if it doesn't exist)
if ! gh release view "v$VERSION" &> /dev/null; then
    print_status "Creating GitHub release v$VERSION..."
    
    # Create release with description
    gh release create "v$VERSION" \
        --title "Soloweb $VERSION" \
        --notes "## Soloweb $VERSION

A production-grade async web framework with zero external dependencies.

### Features
- ✅ Async by default
- ✅ Zero external dependencies  
- ✅ Web-like API
- ✅ Production ready
- ✅ Type hints
- ✅ CORS support
- ✅ Session management
- ✅ Error handling

### Installation
\`\`\`bash
pip install soloweb
\`\`\`

### Quick Start
\`\`\`python
from soloweb import app, route, run

@route('/')
async def hello(request):
    return \"Hello, Soloweb!\"

if __name__ == '__main__':
    run(debug=True)
\`\`\`

### Changes
See CHANGELOG.md for detailed changes."
else
    print_status "Release v$VERSION already exists, skipping creation."
fi

# Upload assets
print_status "Uploading distribution files..."
for file in dist/*; do
    print_status "Uploading $(basename $file)..."
    gh release upload "v$VERSION" "$file" --clobber
    print_success "Uploaded $(basename $file)"
done

# Update README with installation instructions
print_status "Updating README with GitHub installation instructions..."

# Create temporary README with updated installation section
cat > README.md.tmp << EOF
# Soloweb - Production-Grade Async Web Framework

A production-grade async web framework for Python that functions like popular web frameworks but is async by default and uses **zero external dependencies**. Built entirely with standard Python libraries.

## 🚀 Features

- **Async by Default**: All route handlers are async and support concurrent operations
- **Zero Dependencies**: Uses only standard Python libraries (no pip install required)
- **Web-like API**: Familiar decorators and patterns for web developers
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
\`\`\`bash
pip install soloweb
\`\`\`

### From GitHub Releases
\`\`\`bash
# Install specific version
pip install https://github.com/$REPO/releases/download/v$VERSION/soloweb-$VERSION-py3-none-any.whl

# Or install from source
pip install git+https://github.com/$REPO.git@v$VERSION
\`\`\`

### Manual Installation
No installation required! Just copy the framework files to your project:

\`\`\`bash
# Copy the framework files
cp soloweb.py your_project/
\`\`\`
EOF

# Append the rest of the README (skip the installation section)
tail -n +$(grep -n "## 🎯 Quick Start" README.md | cut -d: -f1) README.md >> README.md.tmp

# Replace original README
mv README.md.tmp README.md

print_success "README updated successfully!"

# Print summary
echo
print_success "🎉 Successfully processed version $VERSION"
echo -e "${GREEN}GitHub release:${NC} https://github.com/$REPO/releases/tag/v$VERSION"
echo -e "${GREEN}Install with:${NC} pip install https://github.com/$REPO/releases/download/v$VERSION/soloweb-$VERSION-py3-none-any.whl"
echo
print_status "Don't forget to commit and push the updated README:"
echo "  git add README.md"
echo "  git commit -m \"Update README with GitHub installation instructions\""
echo "  git push" 