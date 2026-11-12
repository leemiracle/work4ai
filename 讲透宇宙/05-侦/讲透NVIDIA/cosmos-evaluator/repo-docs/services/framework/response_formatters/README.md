# Response Formatters

Response formatters for HTTP APIs, providing standardized ways to format and return responses.

| Name                        | Description                                                                                 |
|-----------------------------|---------------------------------------------------------------------------------------------|
| [**JsonResponseFormatter**](#jsonresponseformatter)    | Formats responses as standard JSON objects, with options for pretty-printing and timestamps.|

Every formatter here returns a complete response body; none of them stream. A service that needs to stream owns its own
event helpers alongside its handler.

## JsonResponseFormatter

The `JsonResponseFormatter` provides standardized JSON API responses with consistent structure, error handling, and optional features like timestamps and pagination.

### Quick Start

```python
from services.framework.response_formatters.json_response_formatter import JsonResponseFormatter

# Create formatter
formatter = JsonResponseFormatter()

# Success response
response = await formatter.format_success(
    data={"user_id": 123, "name": "John Doe"},
    metadata={"request_id": "abc-123"}
)
# Returns: JSONResponse with {"success": true, "data": {...}, "metadata": {...}, "timestamp": "..."}

# Error response
response = await formatter.format_error(
    error=ValueError("Invalid input"),
    status_code=400
)
# Returns: JSONResponse with {"success": false, "error": {...}, "timestamp": "..."}

# Progress response
response = await formatter.format_progress(75.0, "Processing data...")
# Returns: JSONResponse with {"success": true, "progress": {...}, "timestamp": "..."}
```

### Configuration Options

```python
# Basic formatter
formatter = JsonResponseFormatter()

# Formatter with pretty printing and no timestamps
formatter = JsonResponseFormatter(
    pretty_print=True,
    include_timestamp=False
)
```

### Response Types

#### Success Responses
```python
# Simple data
await formatter.format_success({"message": "Hello World"})

# With metadata
await formatter.format_success(
    data={"items": [1, 2, 3]},
    metadata={"total": 3, "page": 1}
)
```

#### Error Responses
```python
# Basic error
await formatter.format_error(Exception("Something went wrong"))

# Custom status code
await formatter.format_error(ValueError("Invalid data"), 422)

# Validation errors
formatter.format_validation_error([
    {"field": "email", "message": "Invalid format"},
    {"field": "age", "message": "Must be positive"}
])
```

#### Pagination Responses
```python
formatter.format_paginated_response(
    items=[{"id": 1}, {"id": 2}],
    total=100,
    page=2,
    page_size=10,
    metadata={"query": "search term"}
)
# Includes pagination metadata: total_pages, has_next, has_prev
```

#### Progress Responses
```python
# Long-running operation progress
await formatter.format_progress(25.0, "Analyzing data...")
await formatter.format_progress(100.0, "Complete!")
```

## Adding New Response Formatters

To add support for additional response formats, implement the `ResponseFormatter` protocol:

1. Create formatter class with `format_success()`, `format_error()`, `format_progress()`, and `get_content_type()` methods
2. Handle response data serialization and formatting
3. Set appropriate HTTP headers and content types
4. Write comprehensive tests

### File Structure for New Formatter

When adding a new response formatter (e.g., XML), create these files:

```bash
services/framework/response_formatters/
├── xml_response_formatter.py          # Main implementation
├── tests/
│   └── xml_response_formatter_test.py  # Unit tests
└── BUILD                              # Update with new target
```
