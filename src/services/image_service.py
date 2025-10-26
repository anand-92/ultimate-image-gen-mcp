"""
Unified image service that orchestrates Gemini and Imagen APIs.
Provides a consistent interface for image generation regardless of the underlying model.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.constants import GEMINI_MODELS, IMAGEN_MODELS
from ..core import sanitize_filename
from ..core.exceptions import ImageProcessingError
from .gemini_client import GeminiClient
from .imagen_client import ImagenClient
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
        # Shorten model name (e.g., gemini-2.5-flash-image -> gemini-flash)
        model_short = self.model.replace("gemini-2.5-flash-image", "gemini-flash").replace("imagen-4-", "img4-")
        # Sanitize and shorten prompt (max 30 chars)
        prompt_snippet = sanitize_filename(self.prompt[:30])
        index_str = f"_{self.index + 1}" if self.index > 0 else ""
        return f"{model_short}_{timestamp}_{prompt_snippet}{index_str}.png"

    def get_size(self) -> int:
        """Get image size in bytes."""
        return len(base64.b64decode(self.image_data))


class ImageService:
    """Unified service for image generation using Gemini or Imagen."""

    def __init__(self, api_key: str, *, enable_enhancement: bool = True, timeout: int = 60):
        """
        Initialize image service.

        Args:
            api_key: API key for Google AI services
            enable_enhancement: Enable automatic prompt enhancement
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.enable_enhancement = enable_enhancement
        self.timeout = timeout

        # Initialize clients
        self.gemini_client = GeminiClient(api_key, timeout)
        self.imagen_client = ImagenClient(api_key, timeout)
        self.prompt_enhancer: PromptEnhancer | None = None

        if enable_enhancement:
            # Prompt enhancer uses the same Gemini client
            self.prompt_enhancer = PromptEnhancer(self.gemini_client)

    async def generate(
        self, prompt: str, *, model: str | None = None, enhance_prompt: bool = True, **kwargs: Any
    ) -> list[ImageResult]:
        """
        Generate images using the appropriate API.

        Args:
            prompt: Text prompt for image generation
            model: Model to use (auto-detected if None)
            enhance_prompt: Whether to enhance the prompt
            **kwargs: Additional parameters (aspect_ratio, number_of_images, etc.)

        Returns:
            List of ImageResult objects
        """
        # Detect which API to use based on model
        if model is None:
            model = "gemini-2.5-flash-image"  # Default to Gemini

        is_gemini = model in GEMINI_MODELS
        is_imagen = model in IMAGEN_MODELS

        if not is_gemini and not is_imagen:
            raise ValueError(f"Unknown model: {model}")

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

        # Generate images using appropriate API
        if is_gemini:
            return await self._generate_with_gemini(prompt, model, original_prompt, kwargs)
        else:
            return await self._generate_with_imagen(prompt, model, original_prompt, kwargs)

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

    async def _generate_with_imagen(
        self, prompt: str, model: str, original_prompt: str, params: dict[str, Any]
    ) -> list[ImageResult]:
        """Generate images using Imagen API."""
        response = await self.imagen_client.generate_image(prompt=prompt, model=model, **params)

        images = response["images"]
        results = []

        for i, image_data in enumerate(images):
            result = ImageResult(
                image_data=image_data,
                prompt=original_prompt,
                model=model,
                index=i,
                metadata={"enhanced_prompt": prompt, "api": "imagen", **params},
            )
            results.append(result)

        return results

    def _build_enhancement_context(self, params: dict[str, Any]) -> dict[str, Any]:
        """Build context for prompt enhancement."""
        context = {}

        if "input_image" in params:
            context["is_editing"] = True

        if params.get("maintainCharacterConsistency"):
            context["maintain_character_consistency"] = True

        if params.get("blendImages"):
            context["blend_images"] = True

        if params.get("useWorldKnowledge"):
            context["use_world_knowledge"] = True

        if "aspect_ratio" in params:
            context["aspect_ratio"] = params["aspect_ratio"]

        return context

    async def close(self) -> None:
        """Close all clients."""
        await self.gemini_client.close()
        await self.imagen_client.close()
