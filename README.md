# Bria SDK

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python SDK for the Bria Engine API, designed to make integrating powerful image editing capabilities into your applications seamless and straightforward.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Async/Sync Support](#asyncsync-support)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

### Core Capabilities

- **Async/Sync Support**: Works seamlessly in both synchronous and asynchronous contexts
- **Type Safety**: Full type hints and Pydantic models for request/response validation
- **Status Polling**: Automatic status checking with configurable timeouts and intervals
- **Exception Handling**: Predefined exception types for different error scenarios
- **ContextVar Support**: Flexible authentication using Python's `ContextVar` for multi-threaded/async environments
- **Retry Support**: Configurable automatic retry logic for handling transient HTTP errors

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

### Basic Example

```python
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.size_editing import ExpandImageRequestPayload

# Initialize the client
bria = BriaClient()

# Expand an image
response = bria.image_editing.expand_image(
    payload=ExpandImageRequestPayload(
        image="https://example.com/image.jpg",
        aspect_ratio="1:1"
    )
)

print(f"Result URL: {response.get_result().image_url}")
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

## Configuration

### Environment Variables

| Variable              | Description              | Required | Default                          |
| --------------------- | ------------------------ | -------- | -------------------------------- |
| `BRIA_ENGINE_API_KEY` | Your Bria Engine API key | Yes\*    | None, can be provided at runtime |
| `BRIA_ENGINE_URL`     | Custom API endpoint      | No       | Production URL                   |

\*Required unless using JWT token authentication

### Custom Authentication

The SDK supports multiple authentication methods:

#### Using API Token (ContextVar)

```python
from contextvars import ContextVar
from bria_client import BriaClient

# Using API token
api_token: ContextVar[str] = ContextVar("bria_engine_api_token", default="your-api-key")
bria = BriaClient(api_token_ctx=api_token)
```

#### Using JWT Token

```python
from contextvars import ContextVar
from bria_client import BriaClient

# Using JWT token
jwt_token: ContextVar[str] = ContextVar("bria_engine_jwt_token", default="your-jwt-token")
bria = BriaClient(jwt_token_ctx=jwt_token)
```

#### Direct String Authentication

```python
from bria_client import BriaClient

# Pass token directly as string
bria = BriaClient(api_token_ctx="your-api-key")
```

### Retry Configuration

The SDK supports automatic retry logic for handling transient HTTP errors using `httpx-retries`. You can configure custom retry strategies when initializing the client:

#### Default (No Retries)

```python
from bria_client import BriaClient

# No retry logic (default behavior)
client = BriaClient()
```

#### Custom Retry Strategy

```python
from bria_client import BriaClient
from httpx_retries import Retry

# Configure retry with custom settings
retry = Retry(
    total=5,              # Maximum number of retry attempts
    backoff_factor=0.5,  # Backoff factor for exponential backoff
    status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
)
bria = BriaClient(retry=retry)
```

#### Retry with Authentication

```python
from bria_client import BriaClient
from httpx_retries import Retry

# Combine retry with authentication
retry = Retry(total=3, backoff_factor=1.0)
bria = BriaClient(api_token_ctx="your-api-key", retry=retry)
```

**Retry Configuration Options:**

- `total`: Maximum number of retry attempts (default: varies by `httpx-retries`)
- `backoff_factor`: Multiplier for exponential backoff between retries
- `status_forcelist`: List of HTTP status codes that should trigger a retry
- Other options available in the `httpx-retries` library

For more information on retry configuration, see the [httpx-retries documentation](https://github.com/valohai/httpx-retries).

## API Reference

### Client Initialization

```python
from bria_client import BriaClient

# Default initialization (uses environment variables)
client = BriaClient()

# With custom authentication
client = BriaClient(api_token_ctx="your-token")

# With retry configuration
from httpx_retries import Retry
retry = Retry(total=5, backoff_factor=0.5)
client = BriaClient(retry=retry)
```

### Image Editing API

All image editing methods are available through the `image_editing` property:

```python
bria = BriaClient()

# Background editing
bria.image_editing.remove_background(payload)
bria.image_editing.replace_background(payload)
bria.image_editing.blur_background(payload)

# Foreground editing
bria.image_editing.erase_foreground(payload)
bria.image_editing.crop_foreground(payload)

# Mask-based editing
bria.image_editing.erase(payload)

# Size and quality editing
bria.image_editing.expand_image(payload)
bria.image_editing.enhance_image(payload)
bria.image_editing.increase_resolution(payload)
```

### Status API

Check the status of operations:

```python
status_response = bria.status.get_status(job_id="your-job-id")
```

## Examples

### Remove Background

```python
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload

bria = BriaClient()

response = bria.image_editing.remove_background(
    payload=RemoveBackgroundRequestPayload(
        image="https://example.com/image.jpg"
    )
)

print(f"Result: {response.get_result().image_url}")
```

### Enhance Image Quality

```python
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.size_editing import EnhanceImageRequestPayload, Resolution

bria = BriaClient()

response = bria.image_editing.enhance_image(
    payload=EnhanceImageRequestPayload(
        image="https://example.com/image.jpg",
        resolution=Resolution.FOUR_MEGA_PIXEL
    )
)

print(f"Enhanced image: {response.get_result().image_url}")
```

### Replace Background

```python
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.background_editing import ReplaceBackgroundRequestPayload

bria = BriaClient()

response = bria.image_editing.replace_background(
    payload=ReplaceBackgroundRequestPayload(
        image="https://example.com/image.jpg",
        background="https://example.com/new-background.jpg"
    )
)

print(f"Result: {response.get_result().image_url}")
```

For more examples, check the [`examples/`](examples/) directory in the repository.

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from bria_client.exceptions.engine_api_exception import (
    EngineAPIException,
    ContentModerationException
)
from bria_client.exceptions.polling_exception import PollingException
from bria_client.exceptions.status_exception import StatusException

try:
    response = bria.image_editing.remove_background(payload)
except ContentModerationException as e:
    print(f"Content moderation failed: {e}")
except EngineAPIException as e:
    print(f"API error: {e}")
except StatusException as e:
    print(f"Status check error: {e}")
except PollingException as e:
    print(f"Polling error: {e}")
```

### Exception Types

- **`EngineAPIException`**: Base exception for API errors
- **`ContentModerationException`**: Raised when content moderation fails
- **`PollingException`**: Raised during status polling errors
- **`StatusException`**: Raised when status check fails
- **`UnknownStatusException`**: Raised for unknown status responses

## Async/Sync Support

All API methods work in both sync and async contexts:

### Synchronous Usage

```python
from bria_client import BriaClient

bria = BriaClient()
response = bria.image_editing.remove_background(payload)
```

### Asynchronous Usage

```python
import asyncio
from bria_client import BriaClient

async def main():
    bria = BriaClient()
    response = await bria.image_editing.remove_background(payload)
    return response

result = asyncio.run(main())
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/bria-ai/bria-sdk.git
cd bria-sdk

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Examples

```bash
# Run a specific example
uv run examples/enhance_image.py

# Run with custom environment
BRIA_ENGINE_API_KEY=your-key uv run examples/enhance_image.py
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

We welcome community feedback and contributions! See [Contributing](#contributing) for more information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass and linting checks succeed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Documentation**: [Bria Engine API Documentation](https://docs.bria.ai)
- **Issues**: [GitHub Issues](https://github.com/bria-ai/bria-sdk/issues)

---

Made with ❤️ by [Bria.ai](https://bria.ai)
