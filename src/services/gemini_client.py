"""
Gemini API client for Gemini 3 Pro Image generation.
Uses the official Google GenAI SDK.
"""

import asyncio
import base64
import io
import logging
from functools import partial
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

from ..config.constants import GEMINI_MODELS
from ..core.exceptions import (
    APIError,
    AuthenticationError,
    ContentPolicyError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini 3 Pro Image API using official Google GenAI SDK."""

    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = genai.Client(api_key=api_key)

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "gemini-3-pro-image-preview",
        reference_images: list[str] | None = None,
        aspect_ratio: str | None = None,
        image_size: str = "2K",
        response_modalities: list[str] | None = None,
        enable_google_search: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate or edit an image using Gemini 3 Pro Image.

        Args:
            prompt: Text prompt for image generation or editing instruction
            model: Model to use (default: gemini-3-pro-image-preview)
            reference_images: List of base64-encoded reference images (up to 14)
            aspect_ratio: Desired aspect ratio (optional)
            image_size: Image resolution (1K, 2K, 4K - default: 2K)
            response_modalities: Response types (TEXT, IMAGE - default: ["TEXT", "IMAGE"])
            enable_google_search: Enable Google Search grounding for real-time data
            **kwargs: Additional parameters

        Returns:
            Dict with 'images' key containing list of base64-encoded image data,
            'thoughts' key for thinking process, and 'text' key for text responses

        Raises:
            APIError: If the API request fails
        """
        model_id = GEMINI_MODELS.get(model, model)

        try:
            # Build contents list with reference images and prompt
            contents: list[Any] = []

            # Add reference images if provided (up to 14)
            if reference_images:
                for ref_image_b64 in reference_images[:14]:  # Limit to max 14
                    # Decode base64 to bytes for PIL Image
                    image_bytes = base64.b64decode(ref_image_b64)
                    image = Image.open(io.BytesIO(image_bytes))
                    contents.append(image)

            # Add text prompt
            contents.append(prompt)

            # Build configuration
            if response_modalities is None:
                response_modalities = ["TEXT", "IMAGE"]

            # Build image config (SDK 1.52+ supports both aspect_ratio and image_size)
            image_config = types.ImageConfig(
                aspect_ratio=aspect_ratio if aspect_ratio else None,
                image_size=image_size if image_size else None
            )

            # Build generation config
            config_args: dict[str, Any] = {
                "response_modalities": response_modalities,
                "image_config": image_config,
            }

            # Add Google Search grounding if enabled
            if enable_google_search:
                config_args["tools"] = [{"google_search": {}}]

            config = types.GenerateContentConfig(**config_args)

            logger.debug(f"Generating image with model: {model_id}")
            logger.debug(f"Contents: {len(contents)} items")
            logger.debug(f"Config: {config}")

            # Generate content using official SDK (run in executor since it's synchronous)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.client.models.generate_content,
                    model=model_id,
                    contents=contents,
                    config=config
                )
            )

            # Extract images, thoughts, and text from response
            extraction_result = self._extract_content_from_response(response)
            images = extraction_result["images"]
            thoughts = extraction_result["thoughts"]
            text_parts = extraction_result["text"]

            if not images and "IMAGE" in response_modalities:
                logger.error("No images extracted from response")
                raise APIError("No image data found in Gemini API response")

            result = {
                "images": images,
                "text": text_parts,
                "thoughts": thoughts,
                "model": model,
            }

            # Include grounding metadata if Google Search was used
            if enable_google_search and hasattr(response, 'grounding_metadata'):
                result["grounding_metadata"] = response.grounding_metadata

            return result

        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            self._handle_exception(e)
            raise APIError(f"Gemini API request failed: {e}") from e

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str = "gemini-flash-latest",
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate text using Gemini (for prompt enhancement).

        Args:
            prompt: Text prompt
            model: Model to use
            system_instruction: Optional system instruction

        Returns:
            Generated text response
        """
        model_id = GEMINI_MODELS.get(model, model)

        try:
            config_args = {}
            if system_instruction:
                config_args["system_instruction"] = system_instruction

            config = types.GenerateContentConfig(**config_args) if config_args else None

            # Run in executor since genai SDK is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.client.models.generate_content,
                    model=model_id,
                    contents=prompt,
                    config=config
                )
            )

            # Extract text from response
            return response.text

        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            raise APIError(f"Gemini text generation failed: {e}") from e

    def _extract_content_from_response(self, response: Any) -> dict[str, Any]:
        """
        Extract images, text, and thoughts from Gemini SDK response.

        The genai SDK automatically handles thought signatures, so we just
        need to extract the content.

        Returns dict with keys:
        - images: List of base64-encoded image data
        - text: List of text strings
        - thoughts: List of thought objects with images and text
        """
        images = []
        text_parts = []
        thoughts = []

        try:
            # Iterate through all parts in the response
            for part in response.parts:
                # Check if this is a thought (thinking process)
                is_thought = getattr(part, 'thought', False)

                # Extract image data using SDK's as_image() method
                if hasattr(part, 'inline_data'):
                    try:
                        image = part.as_image()
                        if image:
                            # Convert PIL Image to base64
                            buffer = io.BytesIO()
                            image.save(buffer, format='PNG')
                            image_b64 = base64.b64encode(buffer.getvalue()).decode()

                            if is_thought:
                                thoughts.append({
                                    "type": "image",
                                    "data": image_b64,
                                    "index": len(thoughts)
                                })
                            else:
                                images.append(image_b64)
                                logger.debug(f"Extracted image from response")
                    except Exception as e:
                        logger.warning(f"Could not extract image from part: {e}")

                # Extract text
                if hasattr(part, 'text') and part.text:
                    if is_thought:
                        thoughts.append({
                            "type": "text",
                            "data": part.text,
                            "index": len(thoughts)
                        })
                    else:
                        text_parts.append(part.text)

        except Exception as e:
            logger.warning(f"Error extracting content from response: {e}")

        return {
            "images": images,
            "text": text_parts,
            "thoughts": thoughts,
        }

    def _handle_exception(self, error: Exception) -> None:
        """Handle exceptions from genai SDK."""
        error_msg = str(error)

        logger.error(f"API request failed: {error_msg}")

        # Try to determine error type from message
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise AuthenticationError(
                "Authentication failed. Please check your Gemini API key."
            )
        elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            raise RateLimitError(
                "Rate limit exceeded. Please try again later."
            )
        elif "safety" in error_msg.lower() or "blocked" in error_msg.lower():
            raise ContentPolicyError(
                "Content was blocked by safety filters. Please modify your prompt."
            )

    async def close(self) -> None:
        """Close the Gemini client (genai SDK handles cleanup automatically)."""
        # genai SDK doesn't require explicit cleanup
        pass
