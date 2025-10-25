# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ultimate Gemini MCP Server** - A production-ready FastMCP server unifying Google's Gemini 2.5 Flash Image and Imagen 4/Fast/Ultra APIs into a single, developer-friendly interface with AI-powered prompt enhancement.

This synthesizes features from three excellent MCP servers:
- **mcp-image** (TypeScript): Prompt enhancement concept
- **nanobanana-mcp-server** (Python/FastMCP): Architecture patterns
- **gemini-imagen-mcp-server** (TypeScript): Imagen integration

## Development Commands

### Setup and Installation
```bash
# Install dependencies (required before development)
uv sync --all-extras

# Install from source
uv sync

# Run locally with dev mode (hot-reload enabled)
fastmcp dev src.server:create_app

# Or run directly
python -m src.server
```

### Testing and Quality
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting (check only)
ruff check src/

# Auto-format code
ruff format src/

# Run all quality checks
ruff check src/ && ruff format src/ && mypy src/ && pytest
```

### Environment Setup
```bash
# Required: Set API key
export GEMINI_API_KEY=your_key_here

# Optional: Enable debug logging
export LOG_LEVEL=DEBUG

# Optional: Change output directory
export OUTPUT_DIR=/path/to/output
```

## Architecture

### Core Design Pattern: Unified API with Dual Backends

The server presents a **single consistent interface** (`ImageService`) that routes to either Gemini or Imagen based on the model name:

```python
# ImageService automatically routes based on model
await image_service.generate(
    prompt="a cat",
    model="gemini-2.5-flash-image"  # → GeminiClient
)

await image_service.generate(
    prompt="a cat",
    model="imagen-4-ultra"  # → ImagenClient
)
```

**Key insight:** The model name is the only routing signal. All other parameters are context-dependent and ignored if not applicable to the chosen API.

### Module Responsibilities

**`config/`** - Settings and constants
- `constants.py`: Model lists, API endpoints, limits (single source of truth)
- `settings.py`: Pydantic settings with environment variable binding

**`core/`** - Framework-agnostic utilities
- `exceptions.py`: Custom exception hierarchy for error categorization
- `validation.py`: Input validation functions (called before API requests)

**`services/`** - Business logic layer
- `gemini_client.py`: Gemini API via `generateContent` endpoint
- `imagen_client.py`: Imagen API via `predict` endpoint
- `prompt_enhancer.py`: Uses Gemini Flash to enhance prompts
- `image_service.py`: **Orchestrator** that unifies both APIs

**`tools/`** - MCP tool definitions
- `generate_image.py`: Main tool, handles all parameters
- `batch_generate.py`: Parallel processing wrapper

**`server.py`** - FastMCP initialization
- Creates app via `create_app()` factory function
- Registers tools and resources
- Entry point for both `python -m src.server` and `uvx`

### Data Flow for Image Generation

1. **MCP Tool** (`generate_image`) receives user request
2. **Validation** (`core/validation.py`) checks all inputs
3. **ImageService** determines Gemini vs Imagen from model name
4. **(Optional) PromptEnhancer** improves prompt using Gemini Flash
5. **API Client** (GeminiClient or ImagenClient) calls Google API
6. **ImageResult** objects created with metadata
7. Images saved to disk with descriptive filenames
8. JSON response returned to MCP client

### API Endpoint Differences (Critical!)

**Gemini 2.5 Flash Image:**
```python
# Uses generateContent endpoint
POST /v1beta/models/{model}:generateContent
{
  "contents": [{
    "parts": [
      {"inline_data": {"mime_type": "image/png", "data": "base64..."}},  # Optional for editing
      {"text": "prompt"}
    ]
  }]
}
# Images returned in: response.candidates[0].content.parts[].inline_data.data
```

**Imagen 4/Fast/Ultra:**
```python
# Uses predict endpoint
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
# Images returned in: predictions[].bytesBase64Encoded
```

**Why this matters:** When debugging API issues or adding features, you must check which endpoint you're working with. They have completely different request/response structures.

## Key Implementation Details

### Model Detection Logic (services/image_service.py:126-130)
```python
is_gemini = model in GEMINI_MODELS  # Check against constants.py
is_imagen = model in IMAGEN_MODELS
# This determines which _generate_with_* method is called
```

### Prompt Enhancement Flow
- Uses `gemini-flash-latest` (non-image model) for text generation
- Enhancement is **optional** and **gracefully degrades** on failure
- Context passed includes: aspect_ratio, is_editing, character_consistency flags
- Original prompt preserved in ImageResult.metadata for comparison

### Parameter Routing
Gemini-only: `input_image`, `maintainCharacterConsistency`, `blendImages`, `useWorldKnowledge`
Imagen-only: `negative_prompt`, `seed`, `person_generation`

**Implementation:** tools/generate_image.py conditionally adds parameters based on model type (lines 112-127).

### Filename Generation Strategy
Format: `{model}_{timestamp}_{prompt_snippet}_{index}.png`
- Timestamp: `%Y%m%d_%H%M%S`
- Prompt snippet: First 50 chars, sanitized (alphanumeric + spaces/dashes)
- Index: Only added for multi-image generations (e.g., `_2`, `_3`)

## Common Development Tasks

### Adding a New Model
```python
# 1. Add to constants.py
GEMINI_MODELS = {
    "gemini-new-model": "gemini-new-model",
}
# or
IMAGEN_MODELS = {
    "imagen-5": "models/imagen-5.0-generate-001",
}

# That's it! Auto-detection handles the rest.
```

### Adding a New Tool Parameter

**If parameter applies to both APIs:**
```python
# 1. Add to tool signature (tools/generate_image.py:27)
async def generate_image_tool(
    prompt: str,
    new_param: str | None = None,
    ...
):
    # 2. Add validation
    if new_param:
        validate_new_param(new_param)  # Create in core/validation.py

    # 3. Add to params dict before generate()
    params["new_param"] = new_param

    # 4. Update docstring
```

**If parameter is API-specific:**
```python
# Add conditional logic like lines 120-127 in generate_image.py
if model.startswith("imagen"):  # or check: model in IMAGEN_MODELS
    params["imagen_only_param"] = value
```

### Adding Validation
```python
# In core/validation.py
def validate_new_feature(value: str) -> None:
    """Validate new feature input."""
    if not value:
        raise ValidationError("Value cannot be empty")
    if len(value) > 100:
        raise ValidationError("Value too long (max 100 chars)")
```

**Pattern:** All validation functions raise `ValidationError` with user-friendly messages. Never return booleans.

### Handling New API Errors
```python
# In services/gemini_client.py or imagen_client.py
if response.status == 403:
    raise AuthenticationError("API key invalid or expired")
elif response.status == 429:
    raise RateLimitError("Rate limit exceeded, try again later")
elif response.status == 400 and "safety" in error_msg:
    raise ContentPolicyError("Content blocked by safety filters")
else:
    raise APIError(f"API request failed: {error_msg}", status_code=response.status)
```

**Pattern:** Use specific exception types from `core/exceptions.py` for proper error categorization.

## Testing Strategy

### Unit Tests (markers: `@pytest.mark.unit`)
- Validation functions
- Filename sanitization
- Settings loading
- Exception hierarchy

### Integration Tests (markers: `@pytest.mark.integration`)
- API client methods (with mocked HTTP)
- ImageService orchestration
- Tool functions end-to-end

### Network Tests (markers: `@pytest.mark.network`)
- Real API calls (requires `GEMINI_API_KEY`)
- Mark with `@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"))`

### Run Specific Test Markers
```bash
pytest -m unit              # Fast, no network
pytest -m integration       # Medium speed
pytest -m network           # Slow, needs API key
```

## Configuration Loading Priority

1. **Environment variables** (highest priority)
2. **`.env` file** in working directory
3. **Default values** in `config/settings.py`

Example:
```python
# settings.py (simplified)
class APISettings(BaseSettings):
    gemini_api_key: str = Field(default="")  # Step 3: default

    model_config = SettingsConfigDict(
        env_file=".env",  # Step 2: .env file
        env_prefix="",
    )

# Step 1: export GEMINI_API_KEY=... (highest priority)
```

## Error Handling Philosophy

**Fail fast with clear messages** - Invalid inputs should raise `ValidationError` before making API calls.

**Graceful degradation** - Prompt enhancement failures don't stop image generation:
```python
try:
    prompt = await enhancer.enhance(prompt)
except Exception as e:
    logger.warning(f"Enhancement failed: {e}")
    # Continue with original prompt
```

**User-friendly error messages** - API errors are categorized (Auth, RateLimit, ContentPolicy) so tools can provide actionable feedback.

## Performance Characteristics

- **Prompt Enhancement:** Adds 2-5 seconds latency (optional, enabled by default)
- **Batch Processing:** Default 8 concurrent requests (`MAX_BATCH_SIZE`)
- **Timeouts:** 60s for generation, 30s for enhancement
- **Image Size:** Gemini images typically 2-5MB, Imagen 1-3MB

**Optimization tip:** Disable enhancement for faster iteration: `enhance_prompt=False`

## Deployment Considerations

### Production Checklist
- Set `LOG_LEVEL=INFO` (default DEBUG is too verbose)
- Configure `OUTPUT_DIR` to persistent storage (not temp directory)
- Monitor API quota (especially if enhancement enabled - uses 2 requests per generation)
- Set `REQUEST_TIMEOUT` based on expected image complexity (default 60s)

### Running as MCP Server
```bash
# Via Claude Desktop config (claude_desktop_config.json)
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-key"
      }
    }
  }
}

# Via Claude Code
claude mcp add ultimate-gemini --env GEMINI_API_KEY=key -- uvx ultimate-gemini-mcp
```

## Troubleshooting Guide

**"No image data found in response"**
- Debug: Set `LOG_LEVEL=DEBUG` and check logs for actual API response
- Check: Model name matches constants.py exactly
- Check: Prompt not blocked (look for safety filter messages)

**"Prompt enhancement failed, using original"**
- This is expected behavior when enhancement service is unavailable
- Verify: API key has quota for `gemini-flash-latest` model
- Not critical: Image generation continues with original prompt

**Import errors after changes**
- Run `uv sync` to refresh dependencies
- Ensure Python >= 3.11 (`python --version`)
- Check for circular imports between services

**Type errors from mypy**
- Most common: Missing type annotations on new functions
- Fix: Add `-> None` or `-> dict[str, Any]` return types
- Settings: See `pyproject.toml` [tool.mypy] for enabled checks

## Code Style Guidelines

**Enforced by ruff:**
- Line length: 100 characters
- Import sorting: isort style
- Type hints: Required for all public functions

**Run before committing:**
```bash
ruff format src/ && ruff check src/ && mypy src/
```

**Settings:** See `pyproject.toml` [tool.ruff] and [tool.mypy] sections

## Resources

- **API Keys:** [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gemini Docs:** [ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
- **FastMCP:** [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **MCP Spec:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)
