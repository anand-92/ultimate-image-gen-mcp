"""
Image service for Gemini 3 Pro Image API.
Provides interface for image generation using Gemini 3 Pro Image.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.constants import GEMINI_MODELS
from ..core import sanitize_filename
from ..core.exceptions import ImageProcessingError
from .gemini_client import GeminiClient
from .prompt_enhancer import PromptEnhancer

logger = logging.getLogger(__name__)


class ImageResult:
    """Container for generated image data and metadata."""

    def __init__(
        self,
        image_data: str,
        prompt: str,
        model: str,
        index: int = 0,
        metadata: dict[str, Any] | None = None,
    ):
        self.image_data = image_data  # Base64-encoded
        self.prompt = prompt
        self.model = model
        self.index = index
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def save(self, output_dir: Path, filename: str | None = None) -> Path:
        """Save image to disk."""
        if filename is None:
            filename = self._generate_filename()

        output_path = output_dir / filename

        try:
            # Decode base64 and save
            image_bytes = base64.b64decode(self.image_data)
            output_path.write_bytes(image_bytes)
            logger.info(f"Saved image to {output_path}")
            return output_path
        except Exception as e:
            raise ImageProcessingError(f"Failed to save image: {e}") from e

    def _generate_filename(self) -> str:
        """Generate clean, short filename."""
        timestamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        # Shorten model name
        model_short = self.model.replace("gemini-3-pro-image-preview", "gemini3").replace(
            "imagen-4-", "img4-"
        )
        # Sanitize and shorten prompt (max 30 chars)
        prompt_snippet = sanitize_filename(self.prompt[:30])
        index_str = f"_{self.index + 1}" if self.index > 0 else ""
        return f"{model_short}_{timestamp}_{prompt_snippet}{index_str}.png"

    def get_size(self) -> int:
        """Get image size in bytes."""
        return len(base64.b64decode(self.image_data))


class ImageService:
    """Service for image generation using Gemini 3 Pro Image."""

    def __init__(self, api_key: str, *, enable_enhancement: bool = True, timeout: int = 60):
        """
        Initialize image service.

        Args:
            api_key: API key for Gemini API
            enable_enhancement: Enable automatic prompt enhancement
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.enable_enhancement = enable_enhancement
        self.timeout = timeout

        # Initialize Gemini client
        self.gemini_client = GeminiClient(api_key, timeout)
        self.prompt_enhancer: PromptEnhancer | None = None

        if enable_enhancement:
            # Prompt enhancer uses the same Gemini client
            self.prompt_enhancer = PromptEnhancer(self.gemini_client)

    async def generate(
        self, prompt: str, *, model: str | None = None, enhance_prompt: bool = True, **kwargs: Any
    ) -> list[ImageResult]:
        """
        Generate images using Gemini 3 Pro Image API.

        Args:
            prompt: Text prompt for image generation
            model: Model to use (default: gemini-3-pro-image-preview)
            enhance_prompt: Whether to enhance the prompt
            **kwargs: Additional parameters (aspect_ratio, reference_images, etc.)

        Returns:
            List of ImageResult objects
        """
        # Use Gemini 3 Pro Image
        if model is None:
            model = "gemini-3-pro-image-preview"

        if model not in GEMINI_MODELS:
            raise ValueError(f"Unknown model: {model}. Only Gemini 3 Pro Image is supported.")

        # Enhance prompt if enabled
        original_prompt = prompt
        enhancement_context = self._build_enhancement_context(kwargs)

        if enhance_prompt and self.enable_enhancement and self.prompt_enhancer:
            try:
                result = await self.prompt_enhancer.enhance_prompt(
                    prompt, context=enhancement_context
                )
                prompt = result["enhanced_prompt"]
                logger.info(f"Prompt enhanced: {len(original_prompt)} -> {len(prompt)} chars")
            except Exception as e:
                logger.warning(f"Prompt enhancement failed: {e}")

        # Generate images using Gemini API
        return await self._generate_with_gemini(prompt, model, original_prompt, kwargs)

    async def _generate_with_gemini(
        self, prompt: str, model: str, original_prompt: str, params: dict[str, Any]
    ) -> list[ImageResult]:
        """Generate images using Gemini API."""
        response = await self.gemini_client.generate_image(prompt=prompt, model=model, **params)

        images = response["images"]
        results = []

        for i, image_data in enumerate(images):
            result = ImageResult(
                image_data=image_data,
                prompt=original_prompt,
                model=model,
                index=i,
                metadata={"enhanced_prompt": prompt, "api": "gemini", **params},
            )
            results.append(result)

        return results

    def _build_enhancement_context(self, params: dict[str, Any]) -> dict[str, Any]:
        """Build context for prompt enhancement."""
        context: dict[str, Any] = {}

        if "reference_images" in params and params["reference_images"]:
            context["has_reference_images"] = True
            context["num_reference_images"] = len(params["reference_images"])

        if "aspect_ratio" in params:
            context["aspect_ratio"] = params["aspect_ratio"]

        if params.get("enable_google_search"):
            context["use_google_search"] = True

        return context

    async def close(self) -> None:
        """Close Gemini client."""
        await self.gemini_client.close()
