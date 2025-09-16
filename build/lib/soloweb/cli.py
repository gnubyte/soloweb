#!/usr/bin/env python3
"""
Command-line interface for Soloweb
"""

import argparse
import sys
import os
from pathlib import Path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Soloweb - Production-Grade Async Web Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  soloweb run app.py                    # Run a Soloweb application
  soloweb run app.py --host 0.0.0.0    # Run on all interfaces
  soloweb run app.py --port 8080       # Run on custom port
  soloweb run app.py --debug           # Run in debug mode
  soloweb --version                    # Show version
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Soloweb %s' % get_version()
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a Soloweb application')
    run_parser.add_argument('app', help='Path to the application file')
    run_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    run_parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    run_parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'run':
        run_app(args.app, args.host, args.port, args.debug)


def get_version():
    """Get the current version"""
    try:
        from soloweb import __version__
        return __version__
    except ImportError:
        return "unknown"


def run_app(app_path, host, port, debug):
    """Run a Soloweb application"""
    app_file = Path(app_path)
    
    if not app_file.exists():
        print(f"Error: Application file '{app_path}' not found")
        sys.exit(1)
    
    # Add the app directory to Python path
    app_dir = app_file.parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    try:
        # Import and run the application
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", app_file)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Check if the module has a run function or app object
        if hasattr(app_module, 'run'):
            app_module.run(host=host, port=port, debug=debug)
        elif hasattr(app_module, 'app'):
            app_module.app.run(host=host, port=port, debug=debug)
        else:
            print("Error: Application file must define a 'run' function or 'app' object")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running application: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 