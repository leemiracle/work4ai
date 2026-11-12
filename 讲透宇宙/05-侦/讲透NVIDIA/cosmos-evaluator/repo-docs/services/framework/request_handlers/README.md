# Request Handlers

Implementations of request handlers for processing and validating HTTP requests.

| Name                   | Description                                                        |
|------------------------|--------------------------------------------------------------------|
| [**JsonRequestHandler**](#jsonrequesthandler) | Handles parsing and validation of JSON payloads using Pydantic.    |

## JsonRequestHandler

The `JsonRequestHandler` provides robust JSON request parsing and validation using Pydantic models.

### Quick Start

```python
from pydantic import BaseModel
from services.framework.request_handlers.json_request_handler import JsonRequestHandler

# Define your data model
class UserRequest(BaseModel):
    name: str
    email: str
    age: int = 18

# Create handler
handler = JsonRequestHandler(UserRequest)

# In your FastAPI endpoint
from fastapi import Request

async def create_user(request: Request):
    try:
        # Parse and validate JSON request
        user_data = await handler.parse(request)

        # user_data is now a validated UserRequest object
        print(f"Name: {user_data.name}")
        print(f"Email: {user_data.email}")
        print(f"Age: {user_data.age}")

        return {"success": True, "user": user_data.dict()}

    except RequestValidationError as e:
        return {"error": e.message, "details": e.details}
```

### Advanced Usage

```python
from typing import List, Optional
from pydantic import BaseModel, Field

# Complex model with validation
class ProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    categories: List[str] = []
    description: Optional[str] = None
    active: bool = True

# Create handler
handler = JsonRequestHandler(ProductRequest)

# Use in endpoint
async def create_product(request: Request):
    product = await handler.parse(request)

    # Access validated data
    if product.price > 1000:
        product.categories.append("premium")

    return {"product_id": 123, "data": product.dict()}
```

### Error Handling

The handler raises `RequestValidationError` with detailed information:

```python
try:
    data = await handler.parse(request)
except RequestValidationError as e:
    # e.message - Human readable error message
    # e.field - Field that caused the error (if applicable)
    # e.value - Invalid value (if applicable)
    # e.details - Full validation details from Pydantic

    return {
        "error": "Validation failed",
        "message": e.message,
        "field": e.field,
        "details": e.details
    }
```

## Adding New Request Handlers

To add support for additional request types, implement the `RequestHandler` protocol:

1. Create handler class with `parse()`, `validate()`, and `get_content_type()` methods
2. Handle content type validation and parsing logic
3. Map errors to `RequestValidationError` exceptions
4. Write comprehensive tests

### File Structure for New Handler

When adding a new request handler (e.g., XML), create these files:

```bash
services/framework/request_handlers/
├── xml_request_handler.py          # Main implementation
├── tests/
│   └── xml_request_handler_test.py  # Unit tests
└── BUILD                           # Update with new target
```

### Testing

```python
@pytest.mark.asyncio
async def test_parse_valid_xml():
    handler = XmlRequestHandler()
    mock_request = AsyncMock()
    mock_request.headers = {"content-type": "application/xml"}
    mock_request.body.return_value = b"<user><name>John</name></user>"

    result = await handler.parse(mock_request)
    assert result == {"name": "John"}
```

### Multi-Format Support

```python
async def create_user(request: Request):
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        user_data = await json_handler.parse(request)
    elif content_type.startswith("application/xml"):
        user_data = await xml_handler.parse(request)
    else:
        return {"error": "Unsupported content type"}

    return {"success": True, "user": user_data}
```
