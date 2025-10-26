#!/usr/bin/env python3
"""
Ultimate Gemini MCP Server - Main Entry Point

Unified MCP server supporting:
- Gemini 2.5 Flash Image (with prompt enhancement and editing)
- Imagen 3, 4, and 4-Ultra (with advanced controls)
- Batch processing, prompt templates, and comprehensive features
"""

import logging
import sys

from fastmcp import FastMCP

from .config import ALL_MODELS, get_settings
from .tools import (
    register_batch_generate_tool,
    register_generate_image_tool,
    register_get_image_tool,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # Important: use stderr for logging in MCP
)

logger = logging.getLogger(__name__)


def create_app() -> FastMCP:
    """
    Create and configure the Ultimate Gemini MCP application.

    This is the factory function used by FastMCP CLI.
    """
    logger.info("Initializing Ultimate Gemini MCP Server...")

    try:
        # Load settings (validates API key)
        settings = get_settings()

        logger.info(f"Output directory: {settings.output_dir}")
        logger.info(f"Prompt enhancement: {settings.api.enable_prompt_enhancement}")
        logger.info(f"Available models: {', '.join(ALL_MODELS.keys())}")

        # Create FastMCP server
        mcp = FastMCP(
            "Ultimate Gemini MCP",
            version="1.0.0",
        )

        # Register tools
        register_generate_image_tool(mcp)
        register_batch_generate_tool(mcp)
        register_get_image_tool(mcp)

        # Add resources
        @mcp.resource("image://latest", mime_type="image/png")
        def get_latest_image() -> bytes:
            """
            Get the most recently generated image.

            Returns:
                Binary PNG image data
            """
            if not settings.output_dir.exists():
                raise FileNotFoundError("No images have been generated yet")

            # Find most recent PNG file
            images = sorted(
                settings.output_dir.glob("*.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if not images:
                raise FileNotFoundError("No images found in output directory")

            return images[0].read_bytes()

        @mcp.resource("models://list")
        def list_models() -> str:
            """List all available image generation models."""
            import json

            models_info = {
                "gemini": {
                    "gemini-2.5-flash-image": {
                        "name": "Gemini 2.5 Flash Image",
                        "description": "Advanced image generation with editing and prompt enhancement",
                        "features": [
                            "Prompt enhancement",
                            "Image editing",
                            "Character consistency",
                            "Multi-image blending",
                            "World knowledge integration",
                        ],
                        "default": True,
                    }
                },
                "imagen": {
                    "imagen-4": {
                        "name": "Imagen 4",
                        "description": "High-quality image generation with improved text rendering",
                        "features": [
                            "Enhanced quality",
                            "Better text rendering",
                            "Negative prompts",
                            "Seed-based reproducibility",
                            "Person generation controls",
                            "Advanced controls",
                        ],
                    },
                    "imagen-4-fast": {
                        "name": "Imagen 4 Fast",
                        "description": "Optimized for faster generation while maintaining good quality",
                        "features": [
                            "Faster generation speed",
                            "Good quality output",
                            "Negative prompts",
                            "Seed-based reproducibility",
                            "Person generation controls",
                            "Cost-effective",
                        ],
                    },
                    "imagen-4-ultra": {
                        "name": "Imagen 4 Ultra",
                        "description": "Highest quality with best prompt adherence",
                        "features": [
                            "Highest quality",
                            "Best prompt adherence",
                            "Professional results",
                            "Enhanced text rendering",
                            "Advanced controls",
                        ],
                    },
                },
            }

            return json.dumps(models_info, indent=2)

        @mcp.resource("settings://config")
        def get_config() -> str:
            """Get current server configuration."""
            import json

            config = {
                "output_directory": str(settings.output_dir),
                "prompt_enhancement_enabled": settings.api.enable_prompt_enhancement,
                "batch_processing_enabled": settings.api.enable_batch_processing,
                "default_gemini_model": settings.api.default_gemini_model,
                "default_imagen_model": settings.api.default_imagen_model,
                "max_batch_size": settings.api.max_batch_size,
                "request_timeout": settings.api.request_timeout,
                "default_aspect_ratio": settings.api.default_aspect_ratio,
                "default_output_format": settings.api.default_output_format,
            }

            return json.dumps(config, indent=2)

        logger.info("Ultimate Gemini MCP Server initialized successfully")
        return mcp

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for direct execution."""
    try:
        logger.info("Starting Ultimate Gemini MCP Server...")

        # Create application
        app = create_app()

        # Run the server (FastMCP handles stdio transport)
        logger.info("Server is ready and listening for MCP requests")
        app.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
