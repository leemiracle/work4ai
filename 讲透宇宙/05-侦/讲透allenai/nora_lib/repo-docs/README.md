# nora_lib

For making and coordinating agents and tools.

There are two sub-projects, `interface` and `impl`

`interface` is for use in open-source projects. It has interfaces for use by agents, but no dependencies on Nora platform code. It publishes a python package named `nora_lib, containing just a subset of the code in the earlier versions of `nora_lib`.

`impl` is for use in the Nora project. It has interface implementations based on the Nora platform. It publishes a python package named `nora_lib-impl`.

# Development

Verify changes using

```
make verify
```

# Publication

You can publish a new version from your branch before merging to main, or from main after merging.

Edit the `version.txt` file with the new version, then run

```
export AI2_NORA_PYPI_TOKEN=<SECRET IN NORA VAULT>
make publish
```

This will publish versions of both `nora_lib` and `nora_lib-impl` with the version number contained in `version.txt`
