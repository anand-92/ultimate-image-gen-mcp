"""
Imagen API client for Imagen 3, 4, and 4-Ultra models.
Uses the predict API endpoint per Google's documentation.
"""

import logging
from typing import Any

import httpx

from ..config.constants import IMAGEN_API_BASE, IMAGEN_MODELS
from ..core.exceptions import (
    APIError,
    AuthenticationError,
    ContentPolicyError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class ImagenClient:
    """Client for Imagen 3/4/Ultra API."""

    def __init__(self, api_key: str, timeout: int = 60):
        """
        Initialize Imagen client.

        Args:
            api_key: Gemini/Google API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = IMAGEN_API_BASE
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "imagen-4-ultra",
        number_of_images: int = 1,
        aspect_ratio: str = "1:1",
        output_format: str = "image/png",
        person_generation: str = "allow_adult",
        negative_prompt: str | None = None,
        seed: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate images using Imagen API.

        Args:
            prompt: Text prompt for image generation
            model: Imagen model to use (imagen-3, imagen-4, imagen-4-ultra)
            number_of_images: Number of images to generate (1-4)
            aspect_ratio: Image aspect ratio
            output_format: Output MIME type (image/jpeg or image/png)
            person_generation: Person generation policy
            negative_prompt: Optional negative prompt
            seed: Optional seed for reproducibility
            **kwargs: Additional parameters

        Returns:
            Dict with 'images' key containing list of base64-encoded images

        Raises:
            APIError: If the API request fails
        """
        model_id = IMAGEN_MODELS.get(model, model)
        url = f"{self.base_url}/{model_id}:predict"

        # Build request body according to Imagen API
        request_body: dict[str, Any] = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "outputMimeType": output_format,
                "sampleCount": number_of_images,
                "personGeneration": person_generation,
                "aspectRatio": aspect_ratio
            }
        }

        # Add optional parameters
        if negative_prompt:
            request_body["instances"][0]["negativePrompt"] = negative_prompt

        if seed is not None:
            request_body["parameters"]["seed"] = seed

        headers = {
            "Content-Type": "application/json",
        }

        try:
            logger.debug(f"Sending request to {url}")
            # Add API key as query parameter
            response = await self.client.post(
                f"{url}?key={self.api_key}",
                json=request_body,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            # Extract images from predictions
            images = self._extract_images(data)

            if not images:
                raise APIError("No image data found in Imagen API response")

            return {
                "images": images,
                "model": model,
                "response": data
            }

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except Exception as e:
            logger.error(f"Imagen API request failed: {e}")
            raise APIError(f"Imagen API request failed: {e}")

    def _extract_images(self, response_data: dict[str, Any]) -> list[str]:
        """Extract base64 image data from Imagen API response."""
        images = []

        try:
            predictions = response_data.get("predictions", [])
            for prediction in predictions:
                # Imagen returns base64 data in bytesBase64Encoded field
                image_data = prediction.get("bytesBase64Encoded")
                if image_data:
                    images.append(image_data)
        except Exception as e:
            logger.warning(f"Error extracting images from response: {e}")

        return images

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        status_code = error.response.status_code
        error_text = error.response.text

        logger.error(f"API request failed with status {status_code}: {error_text}")

        if status_code == 401 or status_code == 403:
            raise AuthenticationError(
                "Authentication failed. Please check your API key.",
                status_code=status_code
            )
        elif status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded. Please try again later.",
                status_code=status_code
            )
        elif status_code == 400 and "SAFETY" in error_text.upper():
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
