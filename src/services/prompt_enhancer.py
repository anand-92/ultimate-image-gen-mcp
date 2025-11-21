"""
Prompt enhancement service using Gemini Flash.
Automatically optimizes prompts for better image generation results.
"""

import logging
from typing import Any

from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


PROMPT_ENHANCEMENT_SYSTEM_INSTRUCTION = """You are an expert prompt engineer for AI image generation models. Your task is to enhance user prompts to produce the best possible results.

Follow these guidelines:
1. Preserve the user's core intent and subject matter
2. Add specific, professional details about:
   - Composition (framing, perspective, angle)
   - Lighting (type, quality, direction, mood)
   - Materials and textures
   - Atmosphere and mood
   - Artistic style (if appropriate)
3. Use photographic and cinematic terminology when relevant
4. Be hyper-specific rather than generic
5. For portraits: describe features, expressions, clothing
6. For scenes: describe environment, weather, time of day
7. Keep prompts concise but detailed (aim for 100-300 words)
8. NEVER use hex color values (like #FF0000). Always describe colors using natural language (e.g., "dark red", "neon blue", "warm amber", "deep crimson")
9. Output ONLY the enhanced prompt, no explanations"""


class PromptEnhancer:
    """Service for enhancing image generation prompts."""

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize prompt enhancer.

        Args:
            gemini_client: Gemini client for text generation
        """
        self.gemini_client = gemini_client

    async def enhance_prompt(
        self,
        original_prompt: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """
        Enhance a prompt for better image generation.

        Args:
            original_prompt: Original user prompt
            context: Optional context (features, image type, etc.)

        Returns:
            Dict with 'enhanced_prompt' and 'original_prompt'
        """
        # Build enhancement instruction
        instruction = self._build_enhancement_instruction(original_prompt, context)

        try:
            enhanced = await self.gemini_client.generate_text(
                prompt=instruction,
                system_instruction=PROMPT_ENHANCEMENT_SYSTEM_INSTRUCTION,
                model="gemini-flash-latest",
            )

            # Clean up the enhanced prompt
            enhanced = enhanced.strip()

            logger.info(f"Enhanced prompt: {len(original_prompt)} -> {len(enhanced)} chars")

            return {
                "original_prompt": original_prompt,
                "enhanced_prompt": enhanced,
            }

        except Exception as e:
            logger.warning(f"Prompt enhancement failed, using original: {e}")
            return {
                "original_prompt": original_prompt,
                "enhanced_prompt": original_prompt,
            }

    def _build_enhancement_instruction(self, prompt: str, context: dict[str, Any] | None) -> str:
        """Build the instruction for prompt enhancement."""
        instruction_parts = [f"Enhance this image generation prompt:\n\n{prompt}"]

        if context:
            # Add context hints
            if context.get("is_editing"):
                instruction_parts.append("\nContext: This is for image editing/modification")

            if context.get("maintain_character_consistency"):
                instruction_parts.append(
                    "\nIMPORTANT: Describe the character with specific, consistent features "
                    "for use across multiple generations"
                )

            if context.get("blend_images"):
                instruction_parts.append(
                    "\nContext: Multiple images will be blended. Describe how elements "
                    "should be composed naturally together"
                )

            if context.get("use_world_knowledge"):
                instruction_parts.append(
                    "\nContext: Include accurate real-world details for historical figures, "
                    "landmarks, or factual scenarios"
                )

            if context.get("aspect_ratio"):
                ratio = context["aspect_ratio"]
                if ratio in ["16:9", "21:9"]:
                    instruction_parts.append("\nFormat: Wide landscape composition")
                elif ratio in ["9:16", "2:3", "3:4"]:
                    instruction_parts.append("\nFormat: Vertical/portrait composition")

        return "\n".join(instruction_parts)


async def create_prompt_enhancer(api_key: str, timeout: int = 30) -> PromptEnhancer:
    """
    Factory function to create prompt enhancer.

    Args:
        api_key: Gemini API key
        timeout: Request timeout

    Returns:
        PromptEnhancer instance
    """
    gemini_client = GeminiClient(api_key=api_key, timeout=timeout)
    return PromptEnhancer(gemini_client)
