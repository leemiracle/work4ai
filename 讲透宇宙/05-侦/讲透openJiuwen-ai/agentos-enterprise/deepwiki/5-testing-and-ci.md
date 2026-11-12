<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agentos-enterprise · page 5 Testing and CI · fetched 2026-11-02 -->

# Testing and CI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ci/run_ci.sh](ci/run_ci.sh)
- [tests/st/test_pipeline.sh](tests/st/test_pipeline.sh)
- [tests/ut/test_build.sh](tests/ut/test_build.sh)

</details>



This page provides an overview of the validation tooling, unit tests, system tests, and continuous integration (CI) workflows located in the `tests/` and `ci/` directories of AgentOS Enterprise.

The validation subsystem ensures that the build scripts, core components, and distribution packages adhere to expected standards before deployment.

For details on unit and system test assertions and execution, see [Unit and System Tests](#5.1).
For details on the CI entrypoint and stage chaining, see [CI Pipeline](#5.2).

```
+-------------------------------------------------------------------+
-                         Testing & CI Architecture                 -
+-------------------------------------------------------------------+
        |
        +---> [ci/run_ci.sh] (CI Pipeline Entrypoint)
        |         |
        |         +---> type=ut ---> [tests/ut/test_build.sh] (Unit Tests)
        |         |
        |         +---> type=st ---> [tests/st/test_pipeline.sh] (System Tests)
        |
        +---> [build/build.sh] (Build Pipeline Validated by ST)
```

Sources: `ci/run_ci.sh` [ci/run_ci.sh:1-63](), `tests/ut/test_build.sh` [tests/ut/test_build.sh:1-13](), `tests/st/test_pipeline.sh` [tests/st/test_pipeline.sh:1-14]()

---

## 5.1. Unit and System Tests

Unit tests (`tests/ut/`) and system tests (`tests/st/`) are written as shell scripts that validate script constants, environment values, and full build pipeline outputs.

- **Unit Tests (`tests/ut/test_build.sh`)**: Sources `build/build.sh` to verify core version strings and package counts (such as `JIUWENSWARM_VERSION`, `OPENYUANRONG_VERSION`, `JIUWENSWARM_PACKAGES`, and `OPENYUANRONG_PACKAGES`).
- **System Tests (`tests/st/test_pipeline.sh`)**: Executes `build/build.sh` and asserts the existence of distribution tarballs (`AgentOS-Client.tgz` and `AgentOS-Server.tgz`) under `build/dist/`.

For full instructions on running tests locally and assertion details, see [Unit and System Tests](#5.1).

Sources: `tests/ut/test_build.sh` [tests/ut/test_build.sh:1-13](), `tests/st/test_pipeline.sh` [tests/st/test_pipeline.sh:1-14]()

---

## 5.2. CI Pipeline

The continuous integration orchestrator `ci/run_ci.sh` provides a unified entrypoint for developers to execute tests locally or in pipeline runners. It supports options to select test types (`--type=ut`, `--type=st`, or `all`) and environment configuration (`--skip_build`).

```
+-------------------------------------------------------------+
-                   ci/run_ci.sh Execution Flow               -
+-------------------------------------------------------------+
   [CLI Input] ---> parse args (--type, --skip_build)
                         |
                         +---> switch (${TEST_TYPE})
                                 |
                                 +---> "ut" ---> run_ut() ---> [tests/ut/test_build.sh]
                                 |
                                 +---> "st" ---> run_st() ---> [tests/st/test_pipeline.sh]
                                 |
                                 +---> "all" ---> run_ut() & run_st()
```

For details on the CI stage chaining and environment initialization, see [CI Pipeline](#5.2).

Sources: `ci/run_ci.sh` [ci/run_ci.sh:1-63]()

---

