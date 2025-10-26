"""
Image generation tool supporting both Gemini and Imagen models.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..core import (
    validate_aspect_ratio,
    validate_image_format,
    validate_model,
    validate_number_of_images,
    validate_prompt,
    validate_seed,
)
from ..services import ImageService

logger = logging.getLogger(__name__)


async def generate_image_tool(
    prompt: str,
    model: str | None = None,
    enhance_prompt: bool = True,
    number_of_images: int = 1,
    aspect_ratio: str = "1:1",
    output_format: str = "png",
    # Gemini-specific options
    input_image_path: str | None = None,
    maintain_character_consistency: bool = False,
    blend_images: bool = False,
    use_world_knowledge: bool = False,
    # Imagen-specific options
    negative_prompt: str | None = None,
    seed: int | None = None,
    # Output options
    save_to_disk: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate images using Gemini or Imagen models.

    Args:
        prompt: Text description for image generation
        model: Model to use (gemini-2.5-flash-image, imagen-3, imagen-4, imagen-4-ultra)
        enhance_prompt: Automatically enhance prompt for better results
        number_of_images: Number of images to generate (1-4)
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
        output_format: Image format (png, jpeg, webp)
        input_image_path: Path to input image for editing (Gemini only)
        maintain_character_consistency: Maintain character features across generations (Gemini)
        blend_images: Enable multi-image blending (Gemini)
        use_world_knowledge: Use real-world knowledge for context (Gemini)
        negative_prompt: What to avoid in the image (Imagen)
        seed: Random seed for reproducibility (Imagen)
        save_to_disk: Save images to output directory

    Returns:
        Dict with generated images and metadata
    """
    # Validate inputs
    validate_prompt(prompt)
    if model:
        validate_model(model)
    validate_number_of_images(number_of_images)
    validate_aspect_ratio(aspect_ratio)
    validate_image_format(output_format)

    if seed is not None:
        validate_seed(seed)
        logger.warning(
            "Note: The seed parameter is not currently supported by Imagen API and will be ignored."
        )

    # Get settings
    settings = get_settings()

    # Determine model
    if model is None:
        model = settings.api.default_gemini_model

    # Initialize image service
    image_service = ImageService(
        api_key=settings.api.gemini_api_key,
        enable_enhancement=settings.api.enable_prompt_enhancement,
        timeout=settings.api.request_timeout,
    )

    try:
        # Prepare parameters based on model type
        params: dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
        }

        # Add input image if provided (Gemini)
        if input_image_path:
            image_path = Path(input_image_path)
            if image_path.exists():
                image_data = base64.b64encode(image_path.read_bytes()).decode()
                params["input_image"] = image_data
            else:
                logger.warning(f"Input image not found: {input_image_path}")

        # Add Gemini-specific options
        if maintain_character_consistency:
            params["maintainCharacterConsistency"] = True
        if blend_images:
            params["blendImages"] = True
        if use_world_knowledge:
            params["useWorldKnowledge"] = True

        # Add Imagen-specific options
        if model.startswith("imagen"):
            params["number_of_images"] = number_of_images
            params["output_format"] = f"image/{output_format}"
            params["person_generation"] = "allow_all"  # Hard-coded to allow all people
            if negative_prompt:
                params["negative_prompt"] = negative_prompt
            if seed is not None:
                params["seed"] = seed

        # Generate images
        results = await image_service.generate(
            prompt=prompt,
            model=model,
            enhance_prompt=enhance_prompt and settings.api.enable_prompt_enhancement,
            **params,
        )

        # Prepare response
        response = {
            "success": True,
            "model": model,
            "prompt": prompt,
            "images_generated": len(results),
            "images": [],
            "metadata": {
                "enhance_prompt": enhance_prompt,
                "aspect_ratio": aspect_ratio,
            },
        }

        # Save images and prepare for MCP response
        for result in results:
            image_info = {
                "index": result.index,
                "size": result.get_size(),
                "timestamp": result.timestamp.isoformat(),
            }

            if save_to_disk:
                # Try to save to output directory, but don't fail if it errors
                try:
                    file_path = result.save(settings.output_dir)
                    image_info["path"] = str(file_path)
                    image_info["filename"] = file_path.name
                    logger.info(f"Saved image to {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to save image to disk: {e}")
                    image_info["save_error"] = str(e)
            else:
                # Only include base64 data when not saving to disk (cloud/serverless scenarios)
                # This prevents token overflow for MCP clients with file system access
                image_info["image_base64"] = result.image_data

            # Add enhanced prompt info
            if "enhanced_prompt" in result.metadata:
                image_info["enhanced_prompt"] = result.metadata["enhanced_prompt"]

            response["images"].append(image_info)

        return response

    finally:
        await image_service.close()


def register_get_image_tool(mcp_server: Any) -> None:
    """Register get_image tool with MCP server."""

    @mcp_server.tool()
    async def get_image(filename: str) -> str:
        """
        Retrieve a generated image by filename and return as base64.

        Args:
            filename: The filename of the image (e.g., "gemini-2.5-flash-image_20251026_055415_a cute orange cat sleeping on a sunny windowsill.png")

        Returns:
            JSON string with base64-encoded image data
        """
        import base64
        import json

        from ..config import get_settings

        settings = get_settings()
        image_path = settings.output_dir / filename

        if not image_path.exists():
            return json.dumps({"success": False, "error": f"Image not found: {filename}"})

        try:
            image_data = base64.b64encode(image_path.read_bytes()).decode()

            return json.dumps(
                {
                    "success": True,
                    "filename": filename,
                    "image_base64": image_data,
                    "size": image_path.stat().st_size,
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


def register_generate_image_tool(mcp_server: Any) -> None:
    """Register generate_image tool with MCP server."""

    @mcp_server.tool()
    async def generate_image(
        prompt: str,
        model: str | None = None,
        enhance_prompt: bool = True,
        number_of_images: int = 1,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        input_image_path: str | None = None,
        maintain_character_consistency: bool = False,
        blend_images: bool = False,
        use_world_knowledge: bool = False,
        negative_prompt: str | None = None,
        seed: int | None = None,
        save_to_disk: bool = True,
    ) -> str:
        """
        Generate images using Google's Gemini or Imagen models.

        Supports both:
        - Gemini 2.5 Flash Image: Advanced image generation with editing, prompt enhancement
        - Imagen 4/Ultra: High-quality image generation with advanced controls

        Args:
            prompt: Text description of the image to generate
            model: Model to use (default: gemini-2.5-flash-image)
            enhance_prompt: Automatically enhance prompt using AI (default: True)
            number_of_images: Number of images to generate, 1-4 (default: 1)
            aspect_ratio: Image aspect ratio like 1:1, 16:9, 9:16 (default: 1:1)
            output_format: Image format: png, jpeg, webp (default: png)
            input_image_path: Path to input image for editing (Gemini only)
            maintain_character_consistency: Maintain character features (Gemini only)
            blend_images: Enable multi-image blending (Gemini only)
            use_world_knowledge: Use real-world knowledge (Gemini only)
            negative_prompt: What to avoid in the image (Imagen only)
            seed: Random seed for reproducibility (NOT SUPPORTED - will be ignored)
            save_to_disk: Save images to disk and return file paths (default: True).
                         When True: Returns file paths only (efficient for MCP clients).
                         When False: Returns base64 image data (for cloud/serverless).

        Available models:
        - gemini-2.5-flash-image (default)
        - imagen-4
        - imagen-4-fast
        - imagen-4-ultra

        Returns:
            JSON string with generation results and either file paths (save_to_disk=True)
            or base64 image data (save_to_disk=False)
        """
        try:
            result = await generate_image_tool(
                prompt=prompt,
                model=model,
                enhance_prompt=enhance_prompt,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                output_format=output_format,
                input_image_path=input_image_path,
                maintain_character_consistency=maintain_character_consistency,
                blend_images=blend_images,
                use_world_knowledge=use_world_knowledge,
                negative_prompt=negative_prompt,
                seed=seed,
                save_to_disk=save_to_disk,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
