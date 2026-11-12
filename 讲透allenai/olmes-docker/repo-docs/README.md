## Code Execution for OLMES

A simple wrapper for exeucting code generation in OLMES. Environments can be deployed to AWS Lambda, or run locally using Docker. Currently supports [BigCodeBench](src/bcb_execution/README.md), [MultiPL-E](src/multiple_execution/README.md) and [DS-1000](src/ds1000_execution/README.md).

```bash
pip install -e .
docker --version # ensure docker is running!
```

**Quick Start**

Manage images directly in Python:

```python
import olmes_docker as od

# Spin up the image (e.g. for BigCodeBench)
env = od.create_environment(
    env_type="bcb", # "bcb", "ds1000", "multipl", ...
    host_port=8080,
    memory_limit="2g",
    cpu_limit=1.0,
    auto_start=True
)

# Get endpoint name
endpoint = env.get_execute_endpoint()
print(f"Endpoint created: {endpoint}")

# Execute a test case
result = env.execute_code(
    solution="def multiply(x, y): return x * y",
    test="assert multiply(3, 4) == 12",
    entry_point="multiply",
    task_id="test_task",
    res_id="test_result"
)
print(f"Execution result: {result}")

# Teardown container
env.stop_container()
```

<details>
<summary>additional examples</summary>

```python
# ds1000
env = od.create_environment(
    env_type="ds1000",
    host_port=8080,
    memory_limit="2g",
    cpu_limit=1.0,
    auto_start=True
)

result = env.execute_code(
    test="""
    def multiply(x, y):
        return x * y
    
    assert multiply(3, 4) == 12
    """,
    res_id="test_result"
)

# multipl-e
env = od.create_environment(
    env_type="multipl",
    host_port=8080,
    memory_limit="2g",
    cpu_limit=1.0,
    auto_start=True
)

result = env.execute_code(
    language="python",
    completion="def multiply(x, y): return x * y",
    test="assert multiply(3, 4) == 12",
    res_id="test_result"
)
```

</details>

<hr />

## Verify Docker

Each container has a sample payload in `src/[benchmark]/sample_payloads/payload.json`. You can test that each sample payload passes with:

```sh
python src/test_payloads.py
```