<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NVTX · page 7 Documentation and Testing · fetched 2026-10-26 -->

# Documentation and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [python/tests/__init__.py](python/tests/__init__.py)
- [python/tests/conftest.py](python/tests/conftest.py)
- [python/tests/cython/test_profiler.pyx](python/tests/cython/test_profiler.pyx)
- [python/tests/test_basic.py](python/tests/test_basic.py)
- [python/tests/test_profiler.py](python/tests/test_profiler.py)
- [tools/CMakeLists.txt](tools/CMakeLists.txt)
- [tools/benchmarks/CMakeLists.txt](tools/benchmarks/CMakeLists.txt)
- [tools/tests/CMakeLists.txt](tools/tests/CMakeLists.txt)
- [tools/tests/nvtx_tests.cpp](tools/tests/nvtx_tests.cpp)

</details>



This page provides an overview of the documentation generation and testing infrastructure within the NVTX project. It covers how the project is documented and the testing frameworks used to ensure code quality across the C++, C, and Python components of NVTX.

For information about implementation details of NVTX itself, see [Implementation Details](#6).

## Testing Architecture Overview

The NVTX project employs a comprehensive testing infrastructure that spans multiple language interfaces and includes both unit tests and performance benchmarks.

```mermaid
graph TD
    subgraph "Testing Infrastructure"
        ctest["CTest<br>Master Test Runner"]
        
        subgraph "C/C++ Testing"
            gtest["Google Test<br>C++ Unit Tests"]
            nvtx_test["NVTX_TEST<br>C++ Component Tests"]
        end
        
        subgraph "Performance Testing"
            gbench["Google Benchmark<br>Performance Tests"]
            nvtx_bench["NVTX_BENCH<br>NVTX Performance Tests"]
            example_bench["EXAMPLE_BENCH<br>Example Benchmarks"]
        end
        
        subgraph "Python Testing"
            pytest["pytest<br>Python Test Runner"]
            test_basic["test_basic.py<br>API Functionality Tests"]
            test_profiler["test_profiler.py<br>Profiler Tests"]
            cy_tests["Cython Tests<br>Extension Module Tests"]
        end
    end
    
    ctest --> gtest
    gtest --> nvtx_test
    
    gbench --> nvtx_bench
    gbench --> example_bench
    
    pytest --> test_basic
    pytest --> test_profiler
    test_profiler --> cy_tests
```

Sources: [tools/tests/CMakeLists.txt:21-63](), [tools/benchmarks/CMakeLists.txt:21-69](), [python/tests/conftest.py:7-22]()

## Documentation Infrastructure

NVTX provides documentation through code comments, README files, and documentation generation tools. While specific documentation generation files weren't included in the provided source files, the project likely follows standard documentation practices for C++ and Python codebases.

```mermaid
graph LR
    subgraph "Documentation Sources"
        code_comments["Source Code Comments"]
        readme_files["README Files"]
        wiki_docs["Wiki Documentation"]
        header_docs["Header File Documentation"]
    end
    
    subgraph "Documentation Tools"
        doxygen["Doxygen<br>C/C++ API Documentation"]
        sphinx["Sphinx<br>Python Documentation"]
        gh_wiki["GitHub Wiki"]
    end
    
    subgraph "Generated Documentation"
        cpp_api_docs["C/C++ API Reference"]
        python_api_docs["Python API Reference"]
        user_guides["User Guides"]
        examples_docs["Examples Documentation"]
    end
    
    code_comments --> doxygen
    header_docs --> doxygen
    doxygen --> cpp_api_docs
    
    code_comments --> sphinx
    readme_files --> sphinx
    sphinx --> python_api_docs
    sphinx --> user_guides
    
    wiki_docs --> gh_wiki
    gh_wiki --> user_guides
    gh_wiki --> examples_docs
```

## C++ Testing Framework

The C++ components of NVTX are tested using Google Test, a popular C++ testing framework. The test infrastructure is configured using CMake, which allows for easy integration with the build system.

```mermaid
graph TD
    subgraph "C++ Testing Components"
        cmake_test["tools/tests/CMakeLists.txt<br>Test Configuration"]
        test_src["nvtx_tests.cpp<br>Test Source Files"]
        nvtx_cpp["nvtx3-cpp<br>C++ API Under Test"]
        
        subgraph "Google Test Framework"
            gtest["GTest<br>Test Framework"]
            gmock["GMock<br>Mocking Framework"]
            gtest_main["GTest Main<br>Test Entry Point"]
        end
    end
    
    cmake_test -- "ConfigureTest()" --> test_src
    test_src -- "target_link_libraries()" --> nvtx_cpp
    test_src -- "target_link_libraries()" --> gtest
    test_src -- "target_link_libraries()" --> gmock
    test_src -- "target_link_libraries()" --> gtest_main
    
    cmake_test -- "add_test()" --> ctest["CTest<br>Test Runner"]
    ctest -- "runs" --> test_executables["Test Executables<br>in /gtests"]
```

Sources: [tools/tests/CMakeLists.txt:21-63](), [tools/tests/nvtx_tests.cpp:21-31]()

### Test Configuration

The C++ tests are configured in the `tools/tests/CMakeLists.txt` file, which:

1. Includes the CTest module for test integration
2. Adds Google Test using CPM (CMake Package Manager)
3. Defines a `ConfigureTest` function to standardize test configuration
4. Creates test targets that link against NVTX and Google Test

The CMake configuration leverages the `ConfigureTest` function, which:
- Creates an executable from the test source files
- Links it with Google Test and NVTX
- Sets output directory to `/gtests`
- Registers the test with CTest

Sources: [tools/tests/CMakeLists.txt:36-44]()

## Performance Benchmarking

NVTX includes a benchmarking infrastructure using Google Benchmark to measure the performance of various components.

```mermaid
graph TD
    subgraph "Benchmarking Components"
        cmake_bench["tools/benchmarks/CMakeLists.txt<br>Benchmark Configuration"]
        
        subgraph "Benchmark Sources"
            example_src["example_benchmark.cpp<br>Example Benchmarks"]
            nvtx_src["nvtx_benchmark.cpp<br>NVTX Performance Tests"]
        end
        
        gbench["Google Benchmark<br>Benchmarking Framework"]
        
        nvtx_cpp["nvtx3-cpp<br>C++ API Under Test"]
    end
    
    cmake_bench -- "ConfigureBench()" --> example_src
    cmake_bench -- "ConfigureBench()" --> nvtx_src
    
    example_src -- "target_link_libraries()" --> gbench
    nvtx_src -- "target_link_libraries()" --> gbench
    
    example_src -- "target_link_libraries()" --> nvtx_cpp
    nvtx_src -- "target_link_libraries()" --> nvtx_cpp
    
    cmake_bench -- "builds" --> benchmark_executables["Benchmark Executables<br>in /gbenchmarks"]
```

Sources: [tools/benchmarks/CMakeLists.txt:21-69]()

### Benchmark Configuration

The benchmarking infrastructure is configured in `tools/benchmarks/CMakeLists.txt`, which:

1. Adds Google Benchmark using CPM
2. Defines a `ConfigureBench` function for standardized benchmark setup
3. Creates benchmark targets for example and NVTX benchmarks

The `ConfigureBench` function:
- Creates an executable from benchmark source files
- Links it with Google Benchmark and NVTX
- Sets output directory to `/gbenchmarks`

Sources: [tools/benchmarks/CMakeLists.txt:43-50]()

## Python Testing Framework

The Python components of NVTX are tested using pytest, a powerful Python testing framework. The tests cover various aspects of the Python API, including basic functionality, the profiler, and Cython extensions.

```mermaid
graph TD
    subgraph "Python Testing Components"
        pytest["pytest<br>Test Runner"]
        
        subgraph "Test Sources"
            test_basic["test_basic.py<br>Basic API Tests"]
            test_profiler_py["test_profiler.py<br>Profiler Tests"]
        end
        
        subgraph "Cython Tests"
            conftest["conftest.py<br>Cython Build Setup"]
            cy_source["test_profiler.pyx<br>Cython Test Source"]
            cy_compiled["test_profiler.so/.pyd<br>Compiled Cython Module"]
        end
        
        nvtx_py["nvtx Python Module<br>Under Test"]
    end
    
    conftest -- "build_cython()" --> cy_source
    cy_source -- "compile" --> cy_compiled
    
    pytest -- "discovers and runs" --> test_basic
    pytest -- "discovers and runs" --> test_profiler_py
    
    test_profiler_py -- "imports" --> cy_compiled
    
    test_basic -- "imports" --> nvtx_py
    test_profiler_py -- "imports" --> nvtx_py
    cy_compiled -- "imports" --> nvtx_py
```

Sources: [python/tests/conftest.py:7-22](), [python/tests/test_basic.py:19-323](), [python/tests/test_profiler.py:1-5](), [python/tests/cython/test_profiler.pyx:19-51]()

### Python Test Structure

The Python tests are organized as follows:

1. `test_basic.py`: Contains parameterized pytest tests that verify the basic functionality of the NVTX Python API, including:
   - Annotations (context managers and decorators)
   - Domain handling
   - Categories
   - Range tracking (start/end and push/pop)
   - Markers
   - Payload support

2. `test_profiler.py`: Tests the profiler functionality by importing and running a Cython test

3. Cython tests:
   - `test_profiler.pyx`: Tests the Cython-specific aspects of the profiler
   - Compiled using the setup in `conftest.py`

Sources: [python/tests/test_basic.py:19-323](), [python/tests/test_profiler.py:1-5](), [python/tests/cython/test_profiler.pyx:19-51]()

### Cython Test Setup

The Cython tests are compiled during pytest configuration using the following process:

1. `conftest.py` defines a `build_cython()` function that:
   - Locates the Cython source files
   - Sets up include paths to NVTX C headers
   - Compiles Cython files using `cythonize`

2. The `pytest_configure` hook runs `build_cython()` before tests are executed

This approach ensures that Cython tests are always up-to-date with the latest source code.

Sources: [python/tests/conftest.py:7-22]()

## Test Coverage

The current testing infrastructure covers various aspects of NVTX functionality:

| Component | Test Type | Test Coverage |
|-----------|-----------|---------------|
| C++ API | Unit Tests | Core API functionality |
| C++ API | Benchmarks | Performance characteristics |
| Python API | Unit Tests | Core API functionality, annotations, domains, ranges |
| Python API | Cython Tests | Profiler functionality |

## Running Tests

### Running C++ Tests

To run the C++ tests:

1. Configure the project with CMake:
   ```
   mkdir build && cd build
   cmake ..
   ```

2. Build and run the tests:
   ```
   make
   ctest
   ```

Alternatively, you can run the test executables directly from the `build/gtests` directory.

### Running Benchmarks

To run the benchmarks:

1. Configure the project with CMake as above
2. Build and run the benchmarks:
   ```
   make
   ./gbenchmarks/NVTX_BENCH
   ./gbenchmarks/EXAMPLE_BENCH
   ```

### Running Python Tests

To run the Python tests:

1. Install the required development dependencies:
   ```
   pip install pytest cython
   ```

2. Run the tests from the repository root:
   ```
   pytest -xvs python/tests
   ```

## Writing Tests

### Writing C++ Tests

New C++ tests should be added to existing test files or created as new files in the `tools/tests` directory. Tests should:

1. Include the Google Test header: `#include <gtest/gtest.h>`
2. Include the NVTX header: `#include <nvtx3/nvtx3.hpp>`
3. Define test fixtures as needed
4. Implement tests using the `TEST_F` or `TEST` macros

Example:
```cpp
#include <gtest/gtest.h>
#include <nvtx3/nvtx3.hpp>

struct NVTX_TestFixture : public ::testing::Test {
    // Setup and teardown as needed
};

TEST_F(NVTX_TestFixture, TestName) {
    // Test implementation
    EXPECT_TRUE(/* condition */);
}
```

### Writing Python Tests

New Python tests should be added to `python/tests` directory, following these guidelines:

1. Use pytest fixtures and parameterization for comprehensive testing
2. For each new feature, add parameterized tests that verify functionality with various inputs
3. For Cython functionality, add tests to the `cython` subdirectory

Example:
```python
import pytest
import nvtx

@pytest.mark.parametrize(
    "message", [None, "test_message"]
)
@pytest.mark.parametrize(
    "color", [None, "red", "blue"]
)
def test_nvtx_feature(message, color):
    # Test implementation
    assert True  # Replace with actual assertion
```

Sources: [python/tests/test_basic.py:26-62]()

---

