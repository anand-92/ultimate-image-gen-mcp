#!/usr/bin/env python3
"""
Deployment entry point for Ultimate Gemini MCP Server.

This wrapper uses absolute imports to avoid relative import issues
when the deployment platform inspects the server.
"""

from src.server import create_app

# Export for FastMCP to find
__all__ = ["create_app"]

# Allow running directly
if __name__ == "__main__":
    from src.server import main
    main()
