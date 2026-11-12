# Test Suite Documentation

This directory contains the test suite for asta-resource-repository, a lightweight document metadata index.

## Test Structure

### LocalIndexDocumentStore Tests
- `test_local_index_store.py` - Complete test suite for YAML-based document metadata storage (61 tests)
  - Document CRUD operations (create, read, update, delete)
  - Search functionality across name, summary, tags, and extra fields
  - Validation (URL format, required fields)
  - Persistence across store instances
  - Concurrent access and file locking
  - Edge cases and error handling

## Running Tests

### Quick Start

Run all tests:
```bash
make test
```

Or directly with pytest:
```bash
uv run pytest tests/ -v
```

**No external dependencies required** - all tests use temporary directories and do not require databases, Docker, or external services.

### Specific Test Execution

Run specific test file:
```bash
uv run pytest tests/test_local_index_store.py -v
```

Run specific test:
```bash
uv run pytest tests/test_local_index_store.py::test_store_document -v
```

Run tests matching a pattern:
```bash
uv run pytest tests/ -k "search" -v
```

### Test Coverage

Run tests with coverage:
```bash
uv run pytest tests/ --cov=src/asta/resources --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

Generate coverage for specific module:
```bash
uv run pytest tests/test_local_index_store.py \
  --cov=src/asta/resources/document_store/local_index \
  --cov-report=html
```

## Test Features

### LocalIndexDocumentStore Tests

**CRUD Operations:**
- Create documents with metadata
- Retrieve documents by URI
- Update documents by re-storing with same URI
- Delete documents
- Check document existence
- List all documents

**Validation:**
- URL format validation (must include protocol scheme: http://, https://, file://)
- Required field validation (summary, URL)
- Namespace validation
- URI format validation

**Search:**
- Search by document name
- Search by summary
- Search by tags
- Search by extra metadata fields
- Case-insensitive search
- Result limiting
- Relevance ranking

**Persistence:**
- Documents persist across store instances
- YAML file is created automatically
- Atomic file operations

**Edge Cases:**
- Empty index handling
- Nonexistent document retrieval
- Duplicate URI handling
- Concurrent access (file locking)

## Test Environment

All tests use:
- **Temporary directories**: Each test creates isolated `.asta/documents/index.yaml` files
- **In-memory operations**: Fast execution
- **No cleanup required**: Temporary directories auto-delete
- **Async fixtures**: Using `pytest-asyncio` for async test support

### Test Fixtures

- `temp_index_path`: Provides temporary directory for index file
- `store`: Creates initialized LocalIndexDocumentStore instance

## Development Workflow

### Running Tests During Development

```bash
# Run tests on file save (requires pytest-watch)
uv run pytest-watch tests/ -v

# Run specific tests during development
uv run pytest tests/test_local_index_store.py::test_search_by_name -v

# Run with output (for debugging)
uv run pytest tests/ -v -s
```

### Adding New Tests

1. Add test function to `test_local_index_store.py`
2. Use `@pytest.mark.asyncio` decorator for async tests
3. Use `store` fixture for initialized document store
4. Use `temp_index_path` fixture for custom store configuration
5. Run tests to verify: `uv run pytest tests/test_local_index_store.py -v`

Example test:
```python
@pytest.mark.asyncio
async def test_my_feature(store):
    """Test description"""
    doc = DocumentMetadata(
        uri="",
        name="Test",
        url="https://example.com/doc.pdf",
        summary="Test document",
        mime_type="application/pdf",
    )

    uri = await store.store(doc)
    assert uri.startswith("asta://test-namespace/document/")
```

## CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest tests/ -v

      - name: Check code quality
        run: |
          uv run black --check src/ tests/
          uv run flake8 src/ tests/
```

**Fast execution**: Tests complete in under 1 second
**No services required**: No PostgreSQL, Docker, or external APIs

## Troubleshooting

### Import errors
- Ensure you're using `uv run` to execute commands
- Verify dependencies: `uv sync`
- Check Python version: `python --version` (should be 3.10+)

### Test failures
- Check file permissions in test directory
- Verify temporary directory is writable
- Run with verbose output: `uv run pytest tests/ -vv`

### Fixture errors
- Ensure `pytest-asyncio` is installed: `uv sync --extra dev`
- Check fixture decorators use `@pytest_asyncio.fixture`

## Test Statistics

- **LocalIndexDocumentStore Tests**: 61 tests
- **Test Categories**:
  - CRUD operations: 8 tests
  - Validation: 6 tests (including various URL protocol tests)
  - Search: 14 tests (simple, FTS5, BM25, ranking)
  - Tag operations: 11 tests
  - Persistence: 4 tests
  - Edge cases: 5 tests
  - Cache sync: 3 tests
  - Update operations: 10 tests
- **Execution time**: ~20 seconds
- **Coverage**: ~95% of local_index.py

## Migration from Previous Versions

This test suite replaces:
- ~~`test_postgres_integration.py`~~ (PostgreSQL backend removed)
- ~~`test_github_unit.py`~~ (GitHub backend removed)
- ~~`test_github_integration.py`~~ (GitHub backend removed)
- ~~`test_rest_api.py`~~ (REST API removed)
- ~~`test_server_integration.py`~~ (Unified server removed)
- ~~`test_docker_integration.py`~~ (Docker removed)

All database and external service dependencies have been eliminated.
