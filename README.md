# Bria Client

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python client library for the Bria Engine API, designed to make integrating powerful image and video editing capabilities into your applications seamless and straightforward. The library provides both synchronous and asynchronous clients with flexible request execution modes.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Examples](#examples)
- [Contributing](#contributing)
- [Support](#support)

## Installation

```bash
pip install bria-client
```

## Quick Start

Set your API key:

```bash
export BRIA_API_TOKEN="your-api-key-here"
```

Basic example:

```python
from bria_client import BriaSyncClient
from bria_client.toolkit.image import Image

client = BriaSyncClient()

# Process an image and get the result immediately
response = client.run(
    endpoint="image/edit/remove_background",
    payload={"image": Image("https://example.com/image.jpg").as_bria_api_input}
)

print(response.result)
```

## Usage Guide

### Two Client Types

Choose the client that fits your use case:

**`BriaSyncClient`** - For simple scripts and traditional applications
```python
from bria_client import BriaSyncClient

client = BriaSyncClient()
response = client.run(endpoint="image/edit/remove_background", payload={...})
```

**`BriaAsyncClient`** - For async applications and concurrent processing
```python
from bria_client import BriaAsyncClient

async with BriaAsyncClient() as client:
    response = await client.run(endpoint="image/edit/remove_background", payload={...})
```

### Three Request Methods

**`.run()`** - Wait for immediate result
```python
# Good for quick operations
response = client.run(endpoint="image/edit/remove_background", payload={...})
print(response.result)
```

**`.submit()`** - Submit and continue working
```python
# Good for long operations - returns immediately with request_id
response = client.submit(endpoint="video/segment/mask_by_prompt", payload={...})
print(f"Submitted: {response.request_id}")
# Do other work...
```

**`.poll()`** - Wait for a submitted request to complete
```python
# Check request status until done
response = client.submit(endpoint="...", payload={...})
final = client.poll(response, interval=2, timeout=300)
print(final.result)
```

### Available Operations

**Image Editing:**
- `image/edit/remove_background` - Remove image background
- `image/edit/replace_background` - Replace image background
- `image/edit/expand` - Expand image canvas
- `image/edit/enhance` - Enhance image quality

**Video Processing:**
- `video/segment/mask_by_prompt` - Generate video masks from text prompts

## Examples

### Basic Usage

```python
from bria_client import BriaSyncClient
from bria_client.toolkit.image import Image

client = BriaSyncClient()

response = client.run(
    endpoint="image/edit/remove_background",
    payload={"image": Image("https://example.com/image.jpg").as_bria_api_input}
)

print(response.result)
```

### Batch Processing

```python
from bria_client import BriaSyncClient
from bria_client.toolkit.image import Image

client = BriaSyncClient()
images = ["image1.jpg", "image2.jpg", "image3.jpg"]

# Submit all requests
responses = [
    client.submit(
        endpoint="image/edit/remove_background",
        payload={"image": Image(img).as_bria_api_input}
    )
    for img in images
]

# Wait for all to complete
results = [client.poll(r, timeout=120) for r in responses]
print(f"Processed {len(results)} images")
```

### Async Processing

```python
import asyncio
from bria_client import BriaAsyncClient
from bria_client.toolkit.image import Image

async def process_images():
    async with BriaAsyncClient() as client:
        tasks = [
            client.run(
                endpoint="image/edit/remove_background",
                payload={"image": Image(url).as_bria_api_input}
            )
            for url in ["image1.jpg", "image2.jpg", "image3.jpg"]
        ]
        return await asyncio.gather(*tasks)

results = asyncio.run(process_images())
```

### Error Handling

```python
try:
    response = client.run(endpoint="...", payload={...}, raise_for_status=True)
    print(response.result)
except TimeoutError:
    print("Request timed out")
except Exception as e:
    print(f"Error: {e}")
```

## Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `uv run pytest`
5. Format code: `uv run ruff format .`
6. Submit a pull request

**Guidelines:**
- Add type hints to new code
- Include tests for new features
- Follow existing code style
- Update documentation as needed

**Found a bug?** [Open an issue](https://github.com/Bria-AI/bria-client/issues) with:
- Description of the problem
- Steps to reproduce
- Python version and environment

## Support

- **Documentation**: [docs.bria.ai](https://docs.bria.ai)
- **Issues**: [GitHub Issues](https://github.com/Bria-AI/bria-client/issues)
- **Examples**: See [`examples/`](examples/) directory

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made by [Bria.ai](https://bria.ai)
