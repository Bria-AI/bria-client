# CHANGELOG

## [Unreleased] - Branch: 19-feat-abstract-client-impl vs main

### Added

- **New client architecture**: `BriaSyncClient` and `BriaAsyncClient` replacing old `BriaClient`
- **Three request methods**: `.run()` for immediate results, `.submit()` for async submission, `.poll()` for status checking
- **Engine abstraction layer**: Flexible HTTP engine system with support for custom implementations
- **Toolkit module**: Helper utilities for images, video, status, and models
- **Improved response handling**: Structured `BriaResponse` with clear request/result separation
- **Integration and unit tests**: Comprehensive test suite for clients and toolkit
- **CI/CD improvements**: Added lint and type checking steps to workflow
- **New examples**: async patterns, multi-process usage, custom clients, and error handling

### Changed

- **API style**: Method-based API → endpoint-based API (e.g., `client.run(endpoint="image/edit/remove_background")`)
- **Request format**: Pydantic models → dictionary payloads
- **Response access**: `.get_result()` method → `.result` property
- **Authentication**: Environment-only → flexible context variable support with custom engine options
- **Project structure**: Feature-based modules → unified client-based architecture
- **Documentation**: Complete README rewrite with clearer usage patterns and examples
- **CI/CD**: Merged workflows, simplified authentication, updated to use `uv tool run pytest`

### Removed

- **Old API modules**: `apis/image_editing/`, `apis/status.py`, and related components
- **Schema classes**: All Pydantic request/response models in `schemas/` directory
- **Legacy components**: `engine_client.py`, old decorators, and root `settings.py`
- **Old examples**: Previous example files replaced with new patterns
- **Separate test workflow**: Merged into main workflow

### Breaking Changes

⚠️ **This is a complete API rewrite. All code using the old `BriaClient` API will need to be updated.**

- No backward compatibility with main branch API
- All import paths changed (`from bria_client import BriaClient` → `from bria_client import BriaSyncClient`)
- Request format completely different (Pydantic models → dictionaries)
- Response format changed (`.get_result()` → `.result`)
- Schema classes removed in favor of plain dictionaries
- Method-based API replaced with endpoint strings
- Authentication mechanism changed

### Migration Guide

#### Before (main branch)
```python
from bria_client import BriaClient
from bria_client.schemas.image_editing_apis.background_editing import RemoveBackgroundRequestPayload

bria = BriaClient()
response = bria.image_editing.remove_background(
    payload=RemoveBackgroundRequestPayload(image="https://example.com/image.jpg")
)
result_url = response.get_result().image_url
```

#### After (this branch)
```python
from bria_client import BriaSyncClient
from bria_client.toolkit.image import Image

client = BriaSyncClient()
response = client.run(
    endpoint="image/edit/remove_background",
    payload={"image": Image("https://example.com/image.jpg").as_bria_api_input}
)
result_url = response.result.image_url
```