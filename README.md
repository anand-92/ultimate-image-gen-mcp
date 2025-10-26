# Ultimate Gemini MCP Server 🎨

> The most comprehensive MCP server for AI image generation, unifying Google's Gemini 2.5 Flash Image and Imagen 4/Ultra models with advanced features.

## ✨ Features

### Unified API Support
- **Gemini 2.5 Flash Image**: Advanced image generation with AI-powered prompt enhancement and editing
- **Imagen 4 & 4-Ultra**: High-quality image generation with professional controls
- Automatic model detection and parameter optimization

### Advanced Capabilities
- 🤖 **AI Prompt Enhancement**: Automatically optimize prompts using Gemini Flash for superior results
- 🎨 **Image Editing**: Modify existing images with natural language instructions
- 🚀 **Batch Processing**: Generate multiple images efficiently with parallel processing
- 🎯 **Character Consistency**: Maintain character features across multiple generations
- 🌍 **World Knowledge**: Integrate accurate real-world context for historical/factual subjects
- 🎭 **Multi-Image Blending**: Combine multiple visual elements naturally
- 🎲 **Reproducible Results**: Use seeds for consistent generation (Imagen)
- ⚫ **Negative Prompts**: Specify what to avoid in images (Imagen)

### Production Ready
- Comprehensive error handling and validation
- Configurable settings via environment variables
- Detailed logging and debugging
- MCP resources for configuration and model information

## 🎬 Showcase - See It In Action

> **Simple prompt → Mind-blowing results** - Watch AI prompt enhancement transform basic ideas into cinematic masterpieces.

### Example: Animal + Spider-Man Raimi Suit Blends

All images generated with **16:9 aspect ratio** and **AI prompt enhancement enabled**.

#### Original Prompt
```
a black shiba inu blended with spiderman raimi suit version
```

**Generated with Imagen 4**
- **Model**: `imagen-4`
- **Enhanced Prompt**: "A wide cinematic landscape composition capturing a hyper-detailed, photorealistic portrait of a Black Shiba Inu merged with the aesthetic of the Raimi Spider-Man suit. The dog's dense, black fur integrates seamlessly with the suit's signature sculpted, rubberized texture, featuring raised silver webbing across its body and limbs..."
- **Size**: 1.47 MB
- **Result**: Cinematic composition with dramatic chiaroscuro lighting

**Generated with Imagen 4 Ultra**
- **Model**: `imagen-4-ultra`
- **Enhanced Prompt**: "A hyper-detailed, photorealistic depiction of a black Shiba Inu fully integrated with the aesthetic and materials of the Tobey Maguire Raimi Spider-Man suit... dramatic, high-contrast Chiaroscuro lighting... heroic, mid-action leap across a rain-slicked urban rooftop..."
- **Size**: 1.59 MB
- **Result**: Ultra-high quality with enhanced material textures and volumetric fog

**Generated with Gemini 2.5 Flash (Nanobanana)**
- **Model**: `gemini-2.5-flash-image`
- **Enhanced Prompt**: "Cinematic wide landscape... formidable Black Shiba Inu hybrid... seamlessly merged with the iconic deep crimson and midnight black textures of the Raimi Spider-Man suit... dynamic, heroic three-quarter pose, mid-leap..."
- **Size**: 1.63 MB
- **Result**: Dynamic hero pose with intense atmospheric effects

---

#### Original Prompt
```
an american wirehair cat blended with spiderman raimi suit version
```

**Generated with Gemini 2.5 Flash (Nanobanana)**
- **Model**: `gemini-2.5-flash-image`
- **Enhanced Prompt**: "An imposing figure: an American Wirehair Cat hybrid, its naturally coarse, mottled fur seamlessly integrated with the iconic Sam Raimi Spider-Man suit... perched atop a rain-slicked, Gothic skyscraper gargoyle... high-contrast chiaroscuro, with powerful blue and red rim lighting..."
- **Size**: 1.62 MB
- **Result**: Gothic noir aesthetic with dramatic gargoyle perch

---

#### Original Prompt
```
a maine coon cat blended with spiderman raimi suit version
```

**Generated with Gemini 2.5 Flash (Nanobanana)**
- **Model**: `gemini-2.5-flash-image`
- **Enhanced Prompt**: "A hyper-detailed, photorealistic cinematic composition of a gigantic Maine Coon cat fused with the specific aesthetics of the Sam Raimi Spider-Man suit... dense fur coat mimics the suit's precise material textures... dramatic low-angle (worm's-eye view) to emphasize monumental scale..."
- **Size**: 1.61 MB
- **Result**: Emphasizes gigantic scale perfect for Maine Coon's natural size

---

### 🔥 Why These Results Are Incredible

1. **Simple Input → Professional Output**: Just a basic description produces cinematic, professionally-lit compositions
2. **Model Variety**: Compare Imagen 4, Imagen 4 Ultra, and Gemini 2.5 Flash results side-by-side
3. **AI Enhancement Magic**: See how prompt enhancement adds lighting, composition, and technical details
4. **Consistent Quality**: All images feature dramatic chiaroscuro lighting, atmospheric effects, and hyper-detailed textures
5. **Model-Specific Strengths**:
   - Imagen 4 Ultra: Maximum quality and material detail
   - Gemini 2.5 Flash: Dynamic poses and creative interpretations
   - Imagen 4: Balanced speed and quality

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- [Google Gemini API key](https://makersuite.google.com/app/apikey) (free)

### Installation

#### Option 1: Using uv (Recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install and run the server
uvx ultimate-gemini-mcp
```

#### Option 2: Using pip
```bash
pip install ultimate-gemini-mcp
```

#### Option 3: From Source
```bash
git clone <repository-url>
cd ultimate-gemini-mcp
uv sync
```

### Configuration

Create a `.env` file in your project directory:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Or set environment variables directly:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## 📖 Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Config file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### With Claude Code (VS Code)

```bash
# Add MCP server to Claude Code
claude mcp add ultimate-gemini --env GEMINI_API_KEY=your-api-key -- uvx ultimate-gemini-mcp
```

### With Cursor

Add to Cursor's MCP configuration (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🎯 Available Models

### Gemini Models
- **gemini-2.5-flash-image** (default): Advanced image generation with prompt enhancement and editing

### Imagen Models
- **imagen-4**: High-quality image generation with improved text rendering
- **imagen-4-fast**: Optimized for faster generation with good quality
- **imagen-4-ultra**: Highest quality with best prompt adherence and professional results

## 🛠️ Tools

### `generate_image`

Generate images using any supported model with comprehensive parameters.

**Parameters:**
- `prompt` (required): Text description of the image
- `model`: Model to use (default: gemini-2.5-flash-image)
- `enhance_prompt`: Automatically enhance prompt (default: true)
- `number_of_images`: Number of images to generate, 1-4 (default: 1)
- `aspect_ratio`: Aspect ratio like 1:1, 16:9, 9:16 (default: 1:1)
- `output_format`: Image format: png, jpeg, webp (default: png)

**Gemini-Specific Parameters:**
- `input_image_path`: Path to input image for editing
- `maintain_character_consistency`: Maintain character features across generations
- `blend_images`: Enable multi-image blending
- `use_world_knowledge`: Use real-world knowledge for context

**Imagen-Specific Parameters:**
- `person_generation`: Person policy: dont_allow, allow_adult, allow_all
- `negative_prompt`: What to avoid in the image
- `seed`: Random seed for reproducibility

**Example:**
```
Generate an image of "a serene mountain landscape at sunset with a lake reflection" using imagen-4-ultra
```

### `batch_generate`

Process multiple prompts efficiently with parallel batch processing.

**Parameters:**
- `prompts` (required): List of text prompts
- `model`: Model to use for all images
- `enhance_prompt`: Enhance all prompts (default: true)
- `aspect_ratio`: Aspect ratio for all images
- `batch_size`: Parallel processing size (default: from config)

**Example:**
```
Batch generate images for these prompts:
1. "minimalist logo design for a tech startup"
2. "modern dashboard UI design"
3. "mobile app wireframe"
```

## 🎨 Advanced Features

### AI Prompt Enhancement

When enabled (default), the server uses Gemini Flash to automatically enhance your prompts:

**Original:** `a cat wearing a space helmet`

**Enhanced:** `A photorealistic portrait of a domestic tabby cat wearing a futuristic space helmet, close-up composition, warm studio lighting, detailed fur texture, reflective helmet visor showing subtle reflections, soft focus background, professional photography style`

This significantly improves image quality without requiring you to be a prompt engineering expert!

### Image Editing

Use natural language to edit existing images (Gemini model):

```
Generate an image with:
- prompt: "Add a red scarf to the person"
- input_image_path: "/path/to/image.jpg"
```

### Character Consistency

Generate the same character in different scenes:

```
Generate an image of "a young wizard in a library, studying ancient books"
with maintain_character_consistency: true
```

Then:
```
Generate an image of "the same young wizard, now in a magical forest"
with maintain_character_consistency: true
```

### Reproducible Results

Use seeds for consistent generation (Imagen models):

```
Generate an image with:
- prompt: "a futuristic cityscape"
- model: "imagen-4-ultra"
- seed: 42
```

Running with the same seed will produce the same image.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `OUTPUT_DIR` | Directory for generated images | `generated_images` |
| `ENABLE_PROMPT_ENHANCEMENT` | Enable AI prompt enhancement | `true` |
| `ENABLE_BATCH_PROCESSING` | Enable batch processing | `true` |
| `DEFAULT_GEMINI_MODEL` | Default Gemini model | `gemini-2.5-flash-image` |
| `DEFAULT_IMAGEN_MODEL` | Default Imagen model | `imagen-4-ultra` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `60` |
| `MAX_BATCH_SIZE` | Maximum parallel batch size | `8` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📚 MCP Resources

### `models://list`
View all available models with descriptions and features.

### `settings://config`
View current server configuration.

## 🎭 Use Cases

### Web Development
- Hero images and banners
- UI/UX mockups and wireframes
- Logo and branding assets
- Placeholder images

### App Development
- App icons and splash screens
- User interface elements
- Marketing materials
- Documentation images

### Content Creation
- Blog post illustrations
- Social media graphics
- Presentation visuals
- Product mockups

### Creative Projects
- Character design iterations
- Concept art exploration
- Style variations
- Scene composition

## 📊 Comparison

| Feature | Gemini 2.5 Flash | Imagen 4/Fast/Ultra |
|---------|------------------|---------------------|
| Prompt Enhancement | ✅ Built-in | ✅ Built-in |
| Image Editing | ✅ Yes | ❌ No |
| Character Consistency | ✅ Yes | ❌ No |
| Multi-Image Blending | ✅ Yes | ❌ No |
| Negative Prompts | ❌ No | ✅ Yes |
| Seed-based Reproducibility | ❌ No | ✅ Yes |
| Person Generation Controls | ❌ No | ✅ Yes |
| Speed Options | Standard | Fast/Standard/Ultra |
| Best For | Editing, iteration, context-aware | Photorealism, final quality, speed |

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Add your API key to `.env` or environment variables
- Get a free key at [Google AI Studio](https://makersuite.google.com/app/apikey)

### "Content blocked by safety filters"
- Modify your prompt to comply with content policies
- Try rephrasing without potentially sensitive content

### "Rate limit exceeded"
- Wait a few moments and try again
- Consider upgrading your API plan for higher limits

### Images not saving
- Check that OUTPUT_DIR exists and is writable
- Verify you have sufficient disk space

## 🤝 Contributing

Contributions are welcome! This project combines the best features from multiple MCP servers:
- mcp-image (TypeScript): Prompt enhancement and editing features
- nanobanana-mcp-server (Python): Architecture and FastMCP integration
- gemini-imagen-mcp-server (TypeScript): Imagen API support and batch processing

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built on the excellent work of:
- [mcp-image](https://github.com/shinpr/mcp-image) - Prompt enhancement concept
- [nanobanana-mcp-server](https://github.com/zhongweili/nanobanana-mcp-server) - FastMCP architecture
- [gemini-imagen-mcp-server](https://github.com/serkanhaslak/gemini-imagen-mcp-server) - Imagen integration

## 🔗 Links

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get your API key
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Ready to create amazing AI-generated images?** Install now and start generating! 🚀
