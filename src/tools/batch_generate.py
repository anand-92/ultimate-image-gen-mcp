"""
Batch image generation tool for processing multiple prompts efficiently.
"""

import asyncio
import json
import logging
from typing import Any

from ..config import MAX_BATCH_SIZE, get_settings
from ..core import validate_batch_size, validate_prompts_list
from .generate_image import generate_image_tool

logger = logging.getLogger(__name__)


async def batch_generate_images(
    prompts: list[str],
    model: str | None = None,
    enhance_prompt: bool = True,
    aspect_ratio: str = "1:1",
    output_format: str = "png",
    batch_size: int | None = None,
    **shared_params: Any,
) -> dict[str, Any]:
    """
    Generate multiple images from a list of prompts.

    Args:
        prompts: List of text prompts
        model: Model to use for all images
        enhance_prompt: Enhance all prompts
        aspect_ratio: Aspect ratio for all images
        output_format: Output format for all images
        batch_size: Number of images to process in parallel (default: from config)
        **shared_params: Additional parameters shared across all generations

    Returns:
        Dict with batch results
    """
    # Validate inputs
    validate_prompts_list(prompts)

    settings = get_settings()
    if batch_size is None:
        batch_size = settings.api.max_batch_size

    validate_batch_size(batch_size, MAX_BATCH_SIZE)

    # Prepare results
    results = {
        "success": True,
        "total_prompts": len(prompts),
        "batch_size": batch_size,
        "completed": 0,
        "failed": 0,
        "results": []
    }

    # Process prompts in batches
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}: {len(batch)} prompts")

        # Create tasks for parallel processing
        tasks = [
            generate_image_tool(
                prompt=prompt,
                model=model,
                enhance_prompt=enhance_prompt,
                aspect_ratio=aspect_ratio,
                output_format=output_format,
                number_of_images=1,
                **shared_params
            )
            for prompt in batch
        ]

        # Execute batch
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for j, result in enumerate(batch_results):
            prompt_index = i + j

            if isinstance(result, Exception):
                logger.error(f"Failed to generate image for prompt {prompt_index}: {result}")
                results["failed"] += 1
                results["results"].append({
                    "prompt_index": prompt_index,
                    "prompt": batch[j],
                    "success": False,
                    "error": str(result)
                })
            else:
                results["completed"] += 1
                results["results"].append({
                    "prompt_index": prompt_index,
                    "prompt": batch[j],
                    **result
                })

    return results


def register_batch_generate_tool(mcp_server: Any) -> None:
    """Register batch_generate tool with MCP server."""

    @mcp_server.tool()
    async def batch_generate(
        prompts: list[str],
        model: str | None = None,
        enhance_prompt: bool = True,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        batch_size: int | None = None,
        person_generation: str = "allow_adult",
        negative_prompt: str | None = None,
    ) -> str:
        """
        Generate multiple images from a list of prompts efficiently.

        Processes prompts in parallel batches for optimal performance.
        All images share the same generation settings.

        Args:
            prompts: List of text descriptions for image generation
            model: Model to use for all images (default: gemini-2.5-flash-image)
            enhance_prompt: Enhance all prompts automatically (default: True)
            aspect_ratio: Aspect ratio for all images (default: 1:1)
            output_format: Image format for all images (default: png)
            batch_size: Parallel batch size (default: from config)
            person_generation: Person policy for Imagen models (default: allow_adult)
            negative_prompt: Negative prompt for Imagen models (optional)

        Returns:
            JSON string with batch results including individual image paths
        """
        try:
            result = await batch_generate_images(
                prompts=prompts,
                model=model,
                enhance_prompt=enhance_prompt,
                aspect_ratio=aspect_ratio,
                output_format=output_format,
                batch_size=batch_size,
                person_generation=person_generation,
                negative_prompt=negative_prompt,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, indent=2)
