#!/usr/bin/env python3
"""
Script to build and upload Soloweb package to GitHub releases
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
import argparse


def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result


def get_version():
    """Get the current version from the package"""
    try:
        with open("soloweb/__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception as e:
        print(f"Error reading version: {e}")
        sys.exit(1)


def build_package():
    """Build the package distribution files"""
    print("Building package...")
    
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/")
    
    # Build package
    run_command("python3 setup.py sdist bdist_wheel")
    
    # Check what was created
    dist_files = list(Path("dist").glob("*"))
    print(f"Created distribution files: {[f.name for f in dist_files]}")
    
    return dist_files


def create_github_release(version, dist_files, token, repo):
    """Create a GitHub release and upload assets"""
    print(f"Creating GitHub release for version {version}...")
    
    # GitHub API endpoints
    api_base = "https://api.github.com"
    releases_url = f"{api_base}/repos/{repo}/releases"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if release already exists
    response = requests.get(releases_url, headers=headers)
    if response.status_code != 200:
        print(f"Error checking releases: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    existing_releases = response.json()
    release_exists = any(release["tag_name"] == f"v{version}" for release in existing_releases)
    
    if release_exists:
        print(f"Release v{version} already exists. Skipping creation.")
        return f"v{version}"
    
    # Create release
    release_data = {
        "tag_name": f"v{version}",
        "name": f"Soloweb {version}",
        "body": f"""## Soloweb {version}

A production-grade async web framework with zero external dependencies.

### Features
- ✅ Async by default
- ✅ Zero external dependencies  
- ✅ Flask-like API
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
""",
        "draft": False,
        "prerelease": False
    }
    
    response = requests.post(releases_url, headers=headers, json=release_data)
    if response.status_code != 201:
        print(f"Error creating release: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    release = response.json()
    print(f"Created release: {release['html_url']}")
    
    # Upload assets
    for dist_file in dist_files:
        print(f"Uploading {dist_file.name}...")
        
        with open(dist_file, "rb") as f:
            upload_url = f"{api_base}/repos/{repo}/releases/{release['id']}/assets"
            params = {"name": dist_file.name}
            
            response = requests.post(
                upload_url,
                headers={**headers, "Content-Type": "application/octet-stream"},
                params=params,
                data=f
            )
            
            if response.status_code != 201:
                print(f"Error uploading {dist_file.name}: {response.status_code}")
                print(response.text)
            else:
                print(f"Successfully uploaded {dist_file.name}")
    
    return f"v{version}"


def update_readme_with_github_install(version, repo):
    """Update README with GitHub installation instructions"""
    print("Updating README with GitHub installation instructions...")
    
    readme_path = "README.md"
    with open(readme_path, "r") as f:
        content = f.read()
    
    # Add GitHub installation section after the existing installation section
    github_install_section = f"""
## 📦 Installation

### From PyPI (when available)
```bash
pip install soloweb
```

### From GitHub Releases
```bash
# Install specific version
pip install https://github.com/{repo}/releases/download/v{version}/soloweb-{version}-py3-none-any.whl

# Or install from source
pip install git+https://github.com/{repo}.git@v{version}
```

### Manual Installation
No installation required! Just copy the framework files to your project:

```bash
# Copy the framework files
cp soloweb.py your_project/
```
"""
    
    # Replace the existing installation section
    lines = content.split('\n')
    new_lines = []
    in_install_section = False
    skip_until_next_section = False
    
    for line in lines:
        if line.startswith('## 📦 Installation'):
            in_install_section = True
            new_lines.append(line)
            new_lines.append(github_install_section.split('\n')[1])  # Skip the ## line
            skip_until_next_section = True
        elif skip_until_next_section and line.startswith('## '):
            skip_until_next_section = False
            new_lines.append(line)
        elif not skip_until_next_section:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    with open(readme_path, "w") as f:
        f.write(new_content)
    
    print("README updated successfully!")


def main():
    parser = argparse.ArgumentParser(description="Upload Soloweb package to GitHub releases")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--skip-build", action="store_true", help="Skip building package")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to GitHub")
    parser.add_argument("--skip-readme", action="store_true", help="Skip updating README")
    
    args = parser.parse_args()
    
    # Get current version
    version = get_version()
    print(f"Current version: {version}")
    
    # Build package
    if not args.skip_build:
        dist_files = build_package()
    else:
        dist_files = list(Path("dist").glob("*"))
        if not dist_files:
            print("No distribution files found. Run without --skip-build first.")
            sys.exit(1)
    
    # Upload to GitHub
    if not args.skip_upload:
        tag = create_github_release(version, dist_files, args.token, args.repo)
    else:
        tag = f"v{version}"
    
    # Update README
    if not args.skip_readme:
        update_readme_with_github_install(version, args.repo)
    
    print(f"\n🎉 Successfully processed version {version}")
    print(f"GitHub release: https://github.com/{args.repo}/releases/tag/{tag}")
    print(f"Install with: pip install https://github.com/{args.repo}/releases/download/{tag}/soloweb-{version}-py3-none-any.whl")


if __name__ == "__main__":
    main() 