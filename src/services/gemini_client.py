"""
Gemini API client for Gemini 2.5 Flash Image generation.
Uses the generateContent API endpoint per Google's documentation.
"""

import base64
import logging
from typing import Any

import httpx

from ..config.constants import GEMINI_API_BASE, GEMINI_MODELS
from ..core.exceptions import (
    APIError,
    AuthenticationError,
    ContentPolicyError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini 2.5 Flash Image API."""

    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = GEMINI_API_BASE
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "gemini-2.5-flash-image",
        input_image: str | None = None,
        aspect_ratio: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate or edit an image using Gemini 2.5 Flash Image.

        Args:
            prompt: Text prompt for image generation or editing instruction
            model: Model to use (default: gemini-2.5-flash-image)
            input_image: Base64-encoded input image for editing (optional)
            aspect_ratio: Desired aspect ratio (optional, influences output)
            **kwargs: Additional parameters

        Returns:
            Dict with 'images' key containing list of base64-encoded image data

        Raises:
            APIError: If the API request fails
        """
        model_id = GEMINI_MODELS.get(model, model)
        url = f"{self.base_url}/models/{model_id}:generateContent"

        # Build request body according to doc.md
        parts: list[dict[str, Any]] = []

        # Add input image if provided (for editing)
        if input_image:
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": input_image
                }
            })

        # Add text prompt (include aspect ratio hint if specified)
        prompt_text = prompt
        if aspect_ratio:
            prompt_text = f"{prompt}. Aspect ratio: {aspect_ratio}"

        parts.append({"text": prompt_text})

        # Build generation config for image generation
        generation_config = {
            "responseModalities": ["Image"]
        }

        # Add aspect ratio to image config if specified
        if aspect_ratio:
            generation_config["imageConfig"] = {
                "aspectRatio": aspect_ratio
            }

        request_body = {
            "contents": [{"parts": parts}],
            "generationConfig": generation_config
        }

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            logger.debug(f"Sending request to {url}")
            logger.debug(f"Request body: {request_body}")
            response = await self.client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {data}")

            # Extract images from response
            images = self._extract_images(data)

            if not images:
                logger.error(f"No images extracted from response. Response structure: {list(data.keys())}")
                if "candidates" in data:
                    logger.error(f"Candidates: {data['candidates']}")
                raise APIError("No image data found in Gemini API response")

            return {"images": images, "model": model, "response": data}

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise APIError(f"Gemini API request failed: {e}")

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str = "gemini-2.0-flash",
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
        url = f"{self.base_url}/models/{model_id}:generateContent"

        request_body = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        if system_instruction:
            request_body["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            text = self._extract_text(data)
            return text

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            raise APIError(f"Gemini text generation failed: {e}")

    def _extract_images(self, response_data: dict[str, Any]) -> list[str]:
        """Extract base64 image data from Gemini API response."""
        images = []

        try:
            candidates = response_data.get("candidates", [])
            for candidate in candidates:
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    # Handle both inline_data and inlineData formats
                    inline_data = part.get("inline_data") or part.get("inlineData")
                    if inline_data:
                        image_data = inline_data.get("data")
                        if image_data:
                            images.append(image_data)
                            logger.debug(f"Extracted image data of length: {len(image_data)}")
        except Exception as e:
            logger.warning(f"Error extracting images from response: {e}")

        return images

    def _extract_text(self, response_data: dict[str, Any]) -> str:
        """Extract text from Gemini API response."""
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                return ""

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            # Concatenate all text parts
            text_parts = [part.get("text", "") for part in parts if "text" in part]
            return "".join(text_parts)

        except Exception as e:
            logger.warning(f"Error extracting text from response: {e}")
            return ""

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        status_code = error.response.status_code
        error_text = error.response.text

        logger.error(f"API request failed with status {status_code}: {error_text}")

        if status_code == 401 or status_code == 403:
            raise AuthenticationError(
                "Authentication failed. Please check your Gemini API key.",
                status_code=status_code
            )
        elif status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded. Please try again later.",
                status_code=status_code
            )
        elif status_code == 400 and ("SAFETY" in error_text.upper() or "BLOCKED" in error_text.upper()):
            raise ContentPolicyError(
                "Content was blocked by safety filters. Please modify your prompt.",
                status_code=status_code
            )
        else:
            raise APIError(
                f"API request failed with status {status_code}: {error_text}",
                status_code=status_code
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
