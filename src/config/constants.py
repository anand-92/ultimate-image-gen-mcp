"""
Constants and model definitions for both Gemini and Imagen APIs.
"""

from typing import Final

# API Endpoints
GEMINI_API_BASE: Final[str] = "https://generativelanguage.googleapis.com/v1beta"
IMAGEN_API_BASE: Final[str] = "https://generativelanguage.googleapis.com/v1beta"

# Gemini Models (generateContent API)
GEMINI_MODELS = {
    "gemini-2.5-flash-image": "gemini-2.5-flash-image",
    "gemini-flash-latest": "gemini-flash-latest",  # For prompt enhancement (non-image)
}

# Imagen Models (predict API)
IMAGEN_MODELS = {
    "imagen-4": "models/imagen-4.0-generate-001",
    "imagen-4-fast": "models/imagen-4.0-fast-generate-001",
    "imagen-4-ultra": "models/imagen-4.0-ultra-generate-001",
}

# All available models
ALL_MODELS = {**GEMINI_MODELS, **IMAGEN_MODELS}

# Default models
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-image"
DEFAULT_IMAGEN_MODEL = "imagen-4-ultra"
DEFAULT_ENHANCEMENT_MODEL = "gemini-flash-latest"

# Aspect ratios
ASPECT_RATIOS = [
    "1:1",   # Square
    "2:3",   # Portrait
    "3:2",   # Landscape
    "3:4",   # Portrait
    "4:3",   # Standard landscape
    "4:5",   # Portrait
    "5:4",   # Landscape
    "9:16",  # Vertical mobile
    "16:9",  # Widescreen
    "21:9",  # Ultrawide
]

# Image formats
IMAGE_FORMATS = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp",
}

# Person generation options (Imagen API)
PERSON_GENERATION_OPTIONS = [
    "dont_allow",
    "allow_adult",
    "allow_all",
]

# Generation limits
MAX_IMAGES_PER_REQUEST = 4
MAX_BATCH_SIZE = 8
MAX_PROMPT_LENGTH = 8192
MAX_NEGATIVE_PROMPT_LENGTH = 1024

# File size limits
MAX_IMAGE_SIZE_MB = 20
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# Timeout settings (in seconds)
DEFAULT_TIMEOUT = 60
ENHANCEMENT_TIMEOUT = 30
BATCH_TIMEOUT = 120

# Output settings
DEFAULT_OUTPUT_DIR = "generated_images"
