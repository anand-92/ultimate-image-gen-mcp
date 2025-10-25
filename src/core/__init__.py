"""Core modules for Ultimate Gemini MCP."""

from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ContentPolicyError,
    FileOperationError,
    ImageProcessingError,
    RateLimitError,
    UltimateGeminiError,
    ValidationError,
)
from .validation import (
    sanitize_filename,
    validate_aspect_ratio,
    validate_base64_image,
    validate_batch_size,
    validate_file_path,
    validate_image_format,
    validate_model,
    validate_negative_prompt,
    validate_number_of_images,
    validate_person_generation,
    validate_prompt,
    validate_prompts_list,
    validate_seed,
)

__all__ = [
    # Exceptions
    "UltimateGeminiError",
    "ConfigurationError",
    "ValidationError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ContentPolicyError",
    "ImageProcessingError",
    "FileOperationError",
    # Validation
    "validate_prompt",
    "validate_negative_prompt",
    "validate_model",
    "validate_aspect_ratio",
    "validate_number_of_images",
    "validate_image_format",
    "validate_person_generation",
    "validate_seed",
    "validate_file_path",
    "validate_base64_image",
    "validate_prompts_list",
    "validate_batch_size",
    "sanitize_filename",
]
