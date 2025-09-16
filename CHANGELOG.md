# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2024-12-19

### Changed
- **BREAKING**: Renamed `AsyncFlask` class to `AsyncWeb` for better branding
- **BREAKING**: Renamed `async_flask.py` to `async_web.py`
- Updated all documentation to use generic "web framework" terminology instead of Flask-specific references
- Changed "Flask-like API" to "Web-like API" throughout documentation
- Updated all examples and guides to use `AsyncWeb` instead of `AsyncFlask`

### Fixed
- Removed all Flask references from codebase while maintaining API compatibility
- Updated package keywords and metadata to reflect generic web framework branding

## [1.2.0] - 2024-01-XX

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Soloweb framework
- Async-by-default web framework with zero external dependencies
- Web-like API with decorators and routing
- Request and Response objects with full HTTP support
- Session management with secure session handling
- Middleware support including CORS middleware
- Error handling with custom error handlers
- Cookie parsing and setting capabilities
- JSON request/response handling
- Form data and multipart upload support
- URL routing with dynamic parameters
- Before/after request hooks
- Command-line interface for running applications
- Comprehensive test suite
- Full documentation and examples

### Features
- **Zero Dependencies**: Uses only standard Python libraries
- **Async by Default**: All operations are non-blocking
- **Production Ready**: Includes security features and error handling
- **Web-like API**: Familiar patterns for web developers
- **Type Hints**: Full type annotation support
- **High Performance**: Efficient routing and concurrent request handling

### Technical Details
- Python 3.7+ support
- MIT License
- Cross-platform compatibility
- Comprehensive test coverage 