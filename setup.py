#!/usr/bin/env python3
"""
Setup script for Soloweb - Production-Grade Async Web Framework
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from the package
def get_version():
    with open("soloweb/__init__.py", "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="soloweb",
    version=get_version(),
    author="Patrick Hastings",
    author_email="patrick@example.com",
    description="A production-grade async web framework with zero external dependencies",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/soloweb",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/soloweb/issues",
        "Documentation": "https://github.com/yourusername/soloweb#readme",
        "Source Code": "https://github.com/yourusername/soloweb",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
    keywords="web framework, async, web-like, zero-dependencies, http, server",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - that's the whole point!
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "soloweb=soloweb.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
    license="MIT",
) 