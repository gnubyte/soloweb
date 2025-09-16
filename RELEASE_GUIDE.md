# Soloweb Release Guide

This guide explains how to build and upload Soloweb packages to GitHub releases.

## 🚀 Quick Upload (Recommended)

### Option 1: Using GitHub CLI (Easiest)

1. **Install GitHub CLI** (if not already installed):
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Or download from: https://cli.github.com/
   ```

2. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```

3. **Run the upload script**:
   ```bash
   ./upload_release.sh
   ```

The script will:
- Build the package
- Create a GitHub release
- Upload distribution files
- Update the README with installation instructions

### Option 2: Using Python Script

1. **Install required Python package**:
   ```bash
   pip install requests
   ```

2. **Get a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` permissions
   - Copy the token

3. **Run the Python upload script**:
   ```bash
   python3 upload_to_github.py --token YOUR_TOKEN --repo owner/repo
   ```

## 📦 Manual Upload Process

If you prefer to do it manually or need more control:

### 1. Build the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python3 setup.py sdist bdist_wheel

# Verify files were created
ls -la dist/
```

### 2. Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Set tag version (e.g., `v1.0.0`)
4. Set release title (e.g., "Soloweb 1.0.0")
5. Add release notes:

```markdown
## Soloweb 1.0.0

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
```bash
pip install soloweb
```

### Quick Start
```python
from soloweb import app, route, run

@route('/')
async def hello(request):
    return "Hello, Soloweb!"

if __name__ == '__main__':
    run(debug=True)
```

### Changes
See CHANGELOG.md for detailed changes.
```

### 3. Upload Assets

1. In the release creation page, drag and drop the files from `dist/`:
   - `soloweb-1.0.0.tar.gz`
   - `soloweb-1.0.0-py3-none-any.whl`

2. Click "Publish release"

### 4. Update README

Add GitHub installation instructions to your README.md:

```markdown
## 📦 Installation

### From PyPI (when available)
```bash
pip install soloweb
```

### From GitHub Releases
```bash
# Install specific version
pip install https://github.com/yourusername/soloweb/releases/download/v1.0.0/soloweb-1.0.0-py3-none-any.whl

# Or install from source
pip install git+https://github.com/yourusername/soloweb.git@v1.0.0
```

### Manual Installation
No installation required! Just copy the framework files to your project:

```bash
# Copy the framework files
cp soloweb.py your_project/
```
```

## 🔄 Updating an Existing Release

### Using GitHub CLI

```bash
# Upload new assets to existing release
gh release upload v1.0.0 dist/* --clobber
```

### Using Python Script

```bash
python3 upload_to_github.py --token YOUR_TOKEN --repo owner/repo --skip-build
```

### Manual Update

1. Go to the existing release on GitHub
2. Click "Edit" 
3. Drag and drop new files or use the "Attach binaries" section
4. Click "Update release"

## 📋 Pre-Release Checklist

Before creating a release:

- [ ] Update version in `soloweb/__init__.py`
- [ ] Update `CHANGELOG.md` with new changes
- [ ] Run tests: `PYTHONPATH=. python3 tests/test_soloweb.py`
- [ ] Test the example app: `PYTHONPATH=. python3 example_app.py`
- [ ] Build package: `python3 setup.py sdist bdist_wheel`
- [ ] Verify distribution files are correct

## 🎯 Installation URLs

After uploading, users can install your package using:

### From GitHub Releases
```bash
# Install wheel file
pip install https://github.com/yourusername/soloweb/releases/download/v1.0.0/soloweb-1.0.0-py3-none-any.whl

# Install source distribution
pip install https://github.com/yourusername/soloweb/releases/download/v1.0.0/soloweb-1.0.0.tar.gz
```

### From Git Repository
```bash
# Install specific version
pip install git+https://github.com/yourusername/soloweb.git@v1.0.0

# Install latest from main branch
pip install git+https://github.com/yourusername/soloweb.git
```

## 🔧 Troubleshooting

### Common Issues

1. **Permission denied when uploading**:
   - Make sure your GitHub token has `repo` permissions
   - Check that you're authenticated with `gh auth status`

2. **Release already exists**:
   - Use `--clobber` flag with GitHub CLI to overwrite assets
   - Or manually edit the existing release

3. **Build fails**:
   - Make sure all required files are present
   - Check that `setup.py` is correct
   - Verify Python version compatibility

4. **Import errors after installation**:
   - Check that the package structure is correct
   - Verify `__init__.py` contains all necessary imports
   - Test with `python3 -c "import soloweb; print('OK')"`

### Getting Help

- Check the GitHub CLI documentation: https://cli.github.com/
- Review GitHub API documentation: https://docs.github.com/en/rest
- Verify your repository settings and permissions

## 🎉 Success!

After a successful upload, your package will be available for installation from GitHub releases, and users can easily install it with pip! 