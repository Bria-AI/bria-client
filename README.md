# Bria SDK

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python SDK for the Bria Engine API, providing powerful image editing capabilities including background removal, object manipulation, image enhancement, and more.

## Features

- **Background Editing**: Remove, replace, or blur backgrounds
- **Foreground Editing**: Replace or crop out foreground objects
- **Mask-Based Editing**: Erase objects and generate fills using masks
- **Size Editing**: Expand images, enhance quality, and increase resolution
- **Async/Sync Support**: Works in both synchronous and asynchronous contexts
- **Status Polling**: Automatic status checking with configurable timeouts
- **Content Moderation**: Built-in content moderation support

## Installation

### Using uv (Recommended)

```bash
uv add bria-sdk
```

### Using pip

```bash
pip install bria-sdk
```

## Quick Start

### Basic Usage

```python
from bria_sdk import BriaSDK
from bria_engine_api.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload

# Initialize the SDK
sdk = BriaSDK()

# Expand an image
response = sdk.engine_apis.image_editing.size.expand_image(
    payload=ExpandImageRequestPayload(
        image="https://example.com/image.jpg",
        aspect_ratio="1:1"
    )
)

print(response)
```

### Environment Setup

Set your API key as an environment variable:

```bash
export BRIA_ENGINE_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
BRIA_ENGINE_API_KEY=your-api-key-here
```

## API Reference

### Background Editing

```python
# Remove background
from bria_engine_api.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload

response = sdk.engine_apis.image_editing.background.remove(
    payload=RemoveBackgroundRequestPayload(image="https://example.com/image.jpg")
)

# Replace background
from bria_engine_api.schemas.image_editing_apis.background_editing import ReplaceBackgroundRequestPayload

response = sdk.engine_apis.image_editing.background.replace(
    payload=ReplaceBackgroundRequestPayload(
        image="https://example.com/image.jpg",
        background="https://example.com/background.jpg"
    )
)

# Blur background
from bria_engine_api.schemas.image_editing_apis.background_editing import BlurBackgroundRequestPayload

response = sdk.engine_apis.image_editing.background.blur(
    payload=BlurBackgroundRequestPayload(image="https://example.com/image.jpg")
)
```

### Foreground Editing

```python
# Replace foreground
from bria_engine_api.schemas.image_editing_apis.foreground_editing import ReplaceForegroundRequestPayload

response = sdk.engine_apis.image_editing.foreground.replace(
    payload=ReplaceForegroundRequestPayload(
        image="https://example.com/image.jpg",
        foreground="https://example.com/foreground.jpg"
    )
)

# Crop out foreground
from bria_engine_api.schemas.image_editing_apis.foreground_editing import CropOutRequestPayload

response = sdk.engine_apis.image_editing.foreground.crop_out(
    payload=CropOutRequestPayload(image="https://example.com/image.jpg")
)
```

### Mask-Based Editing

```python
# Erase objects using masks
from bria_engine_api.schemas.image_editing_apis.mask_based_editing import ObjectEraserRequestPayload

response = sdk.engine_apis.image_editing.masks.erase(
    payload=ObjectEraserRequestPayload(
        image="https://example.com/image.jpg",
        mask="https://example.com/mask.jpg"
    )
)

# Generate fills
from bria_engine_api.schemas.image_editing_apis.mask_based_editing import ObjectGenFillRequestPayload

response = sdk.engine_apis.image_editing.masks.gen_fill(
    payload=ObjectGenFillRequestPayload(
        image="https://example.com/image.jpg",
        mask="https://example.com/mask.jpg",
        prompt="a beautiful sunset"
    )
)

# Get masks for an image
from bria_engine_api.schemas.image_editing_apis.mask_based_editing import GetMasksRequestPayload

response = sdk.engine_apis.image_editing.masks.get_masks(
    payload=GetMasksRequestPayload(image="https://example.com/image.jpg")
)
```

### Size Editing

```python
# Expand image
from bria_engine_api.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload

response = sdk.engine_apis.image_editing.size.expand_image(
    payload=ExpandImageRequestPayload(
        image="https://example.com/image.jpg",
        aspect_ratio="16:9"
    )
)

# Enhance image quality
from bria_engine_api.schemas.image_editing_apis.size_editing import EnhanceImageRequestPayload

response = sdk.engine_apis.image_editing.size.enhance_image(
    payload=EnhanceImageRequestPayload(image="https://example.com/image.jpg")
)

# Increase resolution
from bria_engine_api.schemas.image_editing_apis.size_editing import IncreaseResolutionRequestPayload

response = sdk.engine_apis.image_editing.size.increase_resolution(
    payload=IncreaseResolutionRequestPayload(image="https://example.com/image.jpg")
)
```

## Configuration

### Environment Variables

- `BRIA_ENGINE_API_KEY`: Your Bria Engine API key (optional, can be provided as `ContextVar` at runtime)
- `BRIA_ENGINE_URL`: Custom API endpoint (optional, defaults to production)

### Custom Authentication

```python
from contextvars import ContextVar
from bria_sdk import BriaSDK

# Using API token
api_token: ContextVar[str] = ContextVar("bria_engine_api_token", default="your-api-key")
sdk = BriaSDK(api_token_ctx=api_token)

# Using JWT token
jwt_token: ContextVar[str] = ContextVar("bria_engine_jwt_token", default="your-jwt-token")
sdk = BriaSDK(jwt_token_ctx=jwt_token)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from bria_engine_api.exceptions.engine_api_exception import EngineAPIException, ContentModerationException
from bria_engine_api.exceptions.polling_exception import PollingException

try:
    response = sdk.engine_apis.image_editing.background.remove(payload)
except ContentModerationException as e:
    print(f"Content moderation failed: {e}")
except EngineAPIException as e:
    print(f"API error: {e}")
except PollingException as e:
    print(f"Polling error: {e}")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/bria-ai/bria-client-sdk.git
cd bria-client-sdk

# Install dependencies
uv sync
```

### Running Examples

```bash
# Run the basic example
uv run examples/use_by_env.py

# Or run with custom environment
BRIA_ENGINE_API_KEY=your-key uv run examples/use_by_env.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Documentation**: [Bria Engine API Documentation](https://docs.bria.ai)
- **Issues**: [GitHub Issues](https://github.com/bria-ai/bria-client-sdk/issues)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
