#!/usr/bin/env python3
"""
Script to run the PPE Detection API server.

Usage:
    python run_api.py                    # Run in development mode
    python run_api.py --production       # Run in production mode
    python run_api.py --workers 4        # Specify number of workers
"""

import argparse
import os
import sys
import uvicorn


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description="Run PPE Detection API server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        default=False,
        help="Run in production mode (disables reload, optimizes settings)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Log level (default: info)"
    )

    args = parser.parse_args()

    # Determine if reload should be enabled
    reload = args.reload or (not args.production)

    # Set environment variables
    if args.production:
        os.environ["DEBUG"] = "false"
    else:
        os.environ["DEBUG"] = "true"

    print("=" * 70)
    print("PPE Detection API Server")
    print("=" * 70)
    print(f"Mode: {'Production' if args.production else 'Development'}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print(f"Auto-reload: {reload}")
    print(f"Log level: {args.log_level}")
    print("=" * 70)
    print()
    print("API Documentation:")
    print(f"  - Swagger UI: http://{args.host}:{args.port}/api/docs")
    print(f"  - ReDoc: http://{args.host}:{args.port}/api/redoc")
    print(f"  - Health Check: http://{args.host}:{args.port}/api/health")
    print("=" * 70)
    print()

    try:
        # Run the server
        uvicorn.run(
            "src.api.main:app",
            host=args.host,
            port=args.port,
            reload=reload,
            workers=args.workers if args.production else 1,
            log_level=args.log_level,
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
