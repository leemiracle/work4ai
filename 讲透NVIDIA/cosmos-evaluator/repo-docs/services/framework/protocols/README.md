# Service Protocols

Protocol interfaces for microservices.

## Protocol
A **Protocol** in Python is a way to define interfaces using structural subtyping (duck typing). Unlike traditional inheritance, protocols define what methods a class should have without requiring explicit inheritance. This allows for flexible, type-safe interfaces that can be implemented by any class that provides the required methods.

### Example:
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

# Any class with a draw() method automatically satisfies this protocol
class Circle:
    def draw(self) -> None:
        print("Drawing circle")
```

For more detailed information about protocols, see the official Python documentation on [protocols](https://docs.python.org/3/library/typing.html#typing.Protocol).

## Available Protocols

| Name              | Description                                                                                   |
|-------------------|----------------------------------------------------------------------------------------------|
| **RequestHandler**    | Interface for parsing and validating HTTP requests.                                           |
| **ResponseFormatter** | Interface for formatting successful, error, and progress HTTP responses.                      |
| **StorageProvider**   | Interface for storing, retrieving, deleting, and listing data.                                |

Implementations of these protocols can be swapped or extended, promoting modularity and testability.
