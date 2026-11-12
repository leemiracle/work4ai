# Tests

This directory contains tests for NVFlow.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run specific test file
uv run pytest tests/test_core.py

# Run with coverage
uv run pytest --cov=nvflow --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py         # Pytest fixtures
├── test_core.py        # Core functionality tests
└── README.md           # This file
```

## Writing Tests

### Unit Tests

Test individual components in isolation:

```python
def test_my_function():
    result = my_function(input_data)
    assert result == expected_output
```

### Integration Tests

Test multiple components working together:

```python
@pytest.mark.integration
def test_workflow_integration(tmp_path):
    # Set up test workflow
    config_path = tmp_path / "config.yaml"
    # ... create config

    # Run workflow
    runner = WorkflowRunner(str(config_path))
    runner.run()

    # Verify results
    assert output_exists()
```

### Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

## Test Coverage

Aim for >80% code coverage for core components.

View coverage report:
```bash
uv run pytest
# Open htmlcov/index.html in browser
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-commit hooks (optional)
