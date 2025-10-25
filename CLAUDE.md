# CLAUDE.md

Development documentation for Claude Code when working with the Ultimate Gemini MCP server.

## Project Overview

This is the **Ultimate Gemini MCP Server** - a unified image generation server that combines the best features from three excellent MCP servers:

1. **mcp-image** (TypeScript): Intelligent prompt enhancement using Gemini Flash, image editing capabilities
2. **nanobanana-mcp-server** (Python/FastMCP): Production-ready architecture, modular design
3. **gemini-imagen-mcp-server** (TypeScript): Imagen 3/4/Ultra support, batch processing, advanced controls

## Architecture

### Core Design Principles

1. **Unified API**: Single interface supporting both Gemini and Imagen models
2. **Automatic Model Detection**: Parameters automatically adapt to the selected model
3. **Production Ready**: Comprehensive error handling, logging, and validation
4. **Modular Architecture**: Clear separation of concerns for maintainability

### Directory Structure

```
ultimate-gemini-mcp/
├── src/
│   ├── config/              # Configuration and constants
│   │   ├── __init__.py
│   │   ├── constants.py     # Model definitions, endpoints, limits
│   │   └── settings.py      # Pydantic settings management
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── exceptions.py    # Custom exception hierarchy
│   │   └── validation.py    # Input validation functions
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── gemini_client.py     # Gemini 2.5 Flash Image API client
│   │   ├── imagen_client.py     # Imagen 3/4/Ultra API client
│   │   ├── prompt_enhancer.py   # AI prompt enhancement
│   │   └── image_service.py     # Unified image service
│   ├── tools/               # MCP tools
│   │   ├── __init__.py
│   │   ├── generate_image.py    # Main image generation tool
│   │   └── batch_generate.py    # Batch processing tool
│   └── server.py            # FastMCP server setup and entry point
├── pyproject.toml           # Project dependencies and configuration
├── .env.example             # Example environment configuration
├── README.md                # User documentation
└── CLAUDE.md                # This file - developer documentation
```

## Key Components

### 1. API Clients

#### GeminiClient (`services/gemini_client.py`)

Handles Gemini 2.5 Flash Image API using the `generateContent` endpoint:
- Image generation with prompt
- Image editing with input_image
- Text generation for prompt enhancement
- Base64 image data handling

**API Format** (from doc.md):
```python
POST /v1beta/models/{model}:generateContent
{
  "contents": [{
    "parts": [
      {"inline_data": {"mime_type": "image/png", "data": "base64..."}},  # Optional
      {"text": "prompt"}
    ]
  }]
}
```

#### ImagenClient (`services/imagen_client.py`)

Handles Imagen 4/Fast/Ultra API using the `predict` endpoint:
- Multiple model support (imagen-4, imagen-4-fast, imagen-4-ultra)
- Advanced parameters: negative_prompt, seed, person_generation
- Aspect ratio and output format control

**API Format** (from doc.md):
```python
POST /v1beta/{model}:predict?key={api_key}
{
  "instances": [{"prompt": "...", "negativePrompt": "..."}],
  "parameters": {
    "sampleCount": 4,
    "aspectRatio": "16:9",
    "personGeneration": "allow_adult",
    "seed": 42
  }
}
```

### 2. Prompt Enhancement

The `PromptEnhancer` service uses Gemini Flash to automatically improve prompts:

**Features:**
- Adds photographic/artistic details
- Improves composition descriptions
- Enhances lighting and material descriptions
- Context-aware enhancements based on generation parameters

**Example:**
```
Input:  "a cat wearing a space helmet"
Output: "A photorealistic portrait of a domestic tabby cat wearing a
         futuristic space helmet, close-up composition, warm studio
         lighting, detailed fur texture, reflective helmet visor..."
```

### 3. Unified Image Service

The `ImageService` (`services/image_service.py`) provides a consistent interface:

```python
async def generate(
    prompt: str,
    model: str | None = None,
    enhance_prompt: bool = True,
    **kwargs
) -> list[ImageResult]
```

- Automatically detects which API to use based on model
- Handles prompt enhancement if enabled
- Returns list of `ImageResult` objects with metadata
- Manages client lifecycle

### 4. Tools

#### generate_image Tool

Main tool supporting all features:
- Both Gemini and Imagen models
- Optional prompt enhancement
- Gemini-specific: image editing, character consistency, blending
- Imagen-specific: negative prompts, seeds, person controls
- Automatic file saving with descriptive names

#### batch_generate Tool

Efficient parallel processing:
- Processes multiple prompts in configurable batches
- Shared parameters across all generations
- Individual error handling
- Progress tracking

## Development Guidelines

### Adding New Features

1. **New API Parameter:**
   - Add to constants if it's a new option
   - Add validation in `core/validation.py`
   - Add to appropriate client method
   - Add to tool parameters
   - Update documentation

2. **New Model:**
   - Add to `GEMINI_MODELS` or `IMAGEN_MODELS` in `constants.py`
   - No other changes needed (automatic detection)

3. **New Tool:**
   - Create in `tools/` directory
   - Implement tool function
   - Create registration function
   - Register in `server.py`

### Testing

```bash
# Install development dependencies
uv sync --all-extras

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting and formatting
ruff check src/
ruff format src/
```

### Running Locally

```bash
# Set up environment
export GEMINI_API_KEY=your_key_here

# Run with FastMCP dev mode
fastmcp dev src.server:create_app

# Or run directly
python -m src.server
```

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run server
python -m src.server
```

## API Integration Notes

### According to doc.md (Google's Official Documentation):

1. **Gemini 2.5 Flash Image**:
   - Uses `generateContent` endpoint
   - Images returned in response as inline_data
   - Supports text + image input for editing
   - SynthID watermark included automatically

2. **Imagen Models**:
   - Uses `predict` endpoint
   - Images returned in `predictions[].bytesBase64Encoded`
   - Advanced parameters: negative prompts, seeds
   - SynthID watermark included automatically

3. **Best Practices** (from doc.md):
   - Be hyper-specific in prompts
   - Provide context and intent
   - Iterate and refine progressively
   - Use photographic/cinematic terminology
   - Use semantic negative prompts (for Imagen)

## Configuration Management

### Settings Loading Priority:

1. Environment variables
2. `.env` file in working directory
3. Default values in settings classes

### Key Settings:

- `GEMINI_API_KEY`: Required API key
- `OUTPUT_DIR`: Where images are saved (default: generated_images/)
- `ENABLE_PROMPT_ENHANCEMENT`: Enable/disable enhancement (default: true)
- `DEFAULT_GEMINI_MODEL`: Default Gemini model
- `DEFAULT_IMAGEN_MODEL`: Default Imagen model

## Error Handling

### Exception Hierarchy:

```
UltimateGeminiError (base)
├── ConfigurationError (startup, settings)
├── ValidationError (input validation)
├── APIError (API requests)
│   ├── AuthenticationError (401/403)
│   ├── RateLimitError (429)
│   └── ContentPolicyError (safety blocks)
├── ImageProcessingError (image operations)
└── FileOperationError (file I/O)
```

### Error Handling Pattern:

1. **Validation**: Fail fast with clear messages
2. **API Errors**: Categorize and provide user-friendly messages
3. **Logging**: Detailed error context for debugging
4. **Recovery**: Graceful degradation (e.g., skip enhancement on failure)

## Performance Considerations

1. **Prompt Enhancement**: Adds ~2-5 seconds but significantly improves results
2. **Batch Processing**: Configurable parallelism (default: 8 concurrent requests)
3. **Image Size**: Gemini images typically larger than Imagen
4. **Timeouts**: 60s default, increase for multiple images

## Common Patterns

### Adding a New Tool Parameter:

```python
# 1. Add to tool function signature
async def generate_image_tool(
    prompt: str,
    new_parameter: str | None = None,  # Add here
    ...
):
    # 2. Add validation
    if new_parameter:
        validate_new_parameter(new_parameter)

    # 3. Use in service call
    results = await image_service.generate(
        prompt=prompt,
        new_parameter=new_parameter,
        ...
    )
```

### Adding a New Service:

```python
# 1. Create service class
class NewService:
    def __init__(self, config):
        self.config = config

    async def do_something(self):
        pass

# 2. Add to image service as needed
# 3. Register in server.py if exposing as tool
```

## Deployment

### Production Checklist:

- [ ] Set `LOG_LEVEL=INFO` (not DEBUG)
- [ ] Configure `OUTPUT_DIR` to persistent storage
- [ ] Set appropriate `REQUEST_TIMEOUT`
- [ ] Configure `MAX_BATCH_SIZE` based on load
- [ ] Monitor API quota usage
- [ ] Set up error alerting
- [ ] Configure log aggregation

### FastMCP Deployment:

```bash
# Direct execution
python -m src.server

# With uv
uvx ultimate-gemini-mcp

# Docker (create Dockerfile as needed)
# Use Python 3.11+ base image
# Install dependencies with uv
# Run server.py as entrypoint
```

## Troubleshooting

### "No image data found in response"

- Check API key validity
- Verify model name is correct
- Check if prompt was blocked by safety filters
- Review API response in debug logs

### "Prompt enhancement failed, using original"

- Normal behavior - server falls back gracefully
- Check Gemini Flash API access
- Verify API key has sufficient quota

### Import errors

- Run `uv sync` to install dependencies
- Verify Python version >= 3.11
- Check PYTHONPATH if running directly

## Contributing

When adding features:

1. Follow existing code structure
2. Add appropriate validation
3. Include error handling
4. Update documentation
5. Add tests if possible
6. Follow ruff formatting (`ruff format .`)

## Resources

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get API keys
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs) - Official API documentation
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - FastMCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
