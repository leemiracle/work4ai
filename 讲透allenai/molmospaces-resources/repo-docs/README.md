# <img src="https://raw.githubusercontent.com/allenai/molmospaces-resources/main/molmospaces_resources/images/ai2_logo.png" width=22> MolmoSpaces-resources

Resource manager for [MolmoSpaces](https://github.com/allenai/molmospaces). Downloads, caches, and symlinks versioned data archives from remote buckets.

- Versioned, read-only download cache with symlink-based install directories
- Eager or on-demand archive extraction with parallel downloads
- Pluggable archive indexing for fast asset lookup
- Fork-resilient: safe to use across multiprocessing workers

## Installation

```bash
pip install molmospaces-resources
```

## Setup example

Data is assumed to be served from a gated Hugging Face dataset repo, so we typically need to pass a valid token:

```python
import os
from molmospaces_resources import HFRemoteStorage, setup_resource_manager

source = HFRemoteStorage("allenai/molmospaces", repo_prefix="mujoco", token=os.environ["HF_TOKEN"])
mgr = setup_resource_manager(
  source,
  symlink_dir=SYMLINK_DIR,
  versions=ASSETS_VERSIONS,
  cache_dir=CACHE_DIR,
)
```

Alternatively, we can use `R2RemoteStorage` for direct bucket access, including `"mujoco-thor-resources"`, `"isaac-thor-resources"`, and `"mujoco-thor-training-data"` (also available for Google Cloud Storage via `GCRemoteStorage` with `"molmospaces-isaac"`, `"molmospaces-mujoco"`, and `"molmobot-data"` buckets):

```python
from molmospaces_resources import R2RemoteStorage, setup_resource_manager

source = R2RemoteStorage("mujoco-thor-resources")  # known bucket name or full URL
mgr = setup_resource_manager(
  source,
  symlink_dir=SYMLINK_DIR,
  versions=ASSETS_VERSIONS,
  cache_dir=CACHE_DIR,
)
```

Optionally, run project-specific logic after setup via `post_setup`:

```python
def my_post_setup(manager):
  ## Install all scenes (while skipping per-file symlinking):
  # manager.install_all_for_data_type("scenes", skip_linking=True)
  
  ## Install all objects (with per-dataset symlinking):
  # manager.install_all_for_data_type("objects")
  pass

mgr = setup_resource_manager(
  source,
  symlink_dir=SYMLINK_DIR,
  versions=ASSETS_VERSIONS,
  cache_dir=CACHE_DIR,
  post_setup=my_post_setup,
  force_post_setup=True,  # run post_setup even if all data sources are configured
)
```

## Logging

By default, Python's logging shows `WARNING` and above, so the library will be quiet. To see detailed progress messages, either configure the root logger:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

or set the `molmospaces_resources` logger level explicitly:

```python
import logging
logger = logging.getLogger("molmospaces_resources")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
```

## FAQ

**FAQ 0\. I'm getting hard to parse errors when using the ResourceManager and I cannot resolve the issue by just erasing the involved subdirectories and the corresponding entries in the installed data manifests (`mjthor_data_type_to_source_to_versions.json`) under both install and cache dirs.**

Chances are it might be easiest to just fully erase both cache and symlink dirs (see the differences between both below) and then start populating new cache and symlink dirs by just setting up the resource manager with the desired data sources and versions (e.g. as described above). Note that some data sources, like thor objects or robots, will get fully extracted during the initial setup, which takes longer than usual to complete.

**FAQ 1\. What is the difference between `cache_dir` and `symlink_dir`?**

The resource manager uses two separate directory trees that must not overlap:

- **`cache_dir`** is the versioned download cache. Archives are extracted into a `<data_type>/<source>/<version>/` hierarchy, and multiple versions can coexist side by side. Files here are set read-only to prevent accidental modification. This directory can be safely shared across containers or workers.

- **`symlink_dir`** is the user-facing install directory. It presents a flat `<data_type>/<source>/` layout with no version in the path — the version is hidden behind symlinks that point into `cache_dir`. This allows application code to use stable, version-agnostic paths while the underlying data can be upgraded by simply re-pointing the symlinks.

These two directories **must resolve to different physical locations** and neither can be nested inside the other. The manager validates this at construction time and raises an error if the paths overlap.

**FAQ 2\. A process hangs waiting for a lock on a shared filesystem (e.g. WekaFS, NFS).**

The resource manager uses file-based locks (`.lock` files) to coordinate concurrent access to the cache and symlink directories. On local filesystems, the OS automatically releases these locks when a process dies. On shared/networked filesystems like WekaFS or NFS, if a container is destroyed without a clean shutdown (e.g. killed by the orchestrator, node crash), the lock may not be released immediately. The filesystem will typically detect the dead client eventually, but this can take a varying amount of time.

If setup appears stuck, you can manually remove the stale lock file (typically in the shared cache directory):

```bash
rm /path/to/cache_dir/.lock
```

If the interrupted process was mid-install, the cache may contain partially extracted archives. The safest recovery is to delete the entire affected `<data_type>/<source>/<version>/` directory under `cache_dir`, remove the corresponding entry from the local manifest files, and re-run setup. Partial cleanup (e.g. removing individual archives) is possible but requires checking the `.complete_extract` / `.complete_links` flag files as well.

In shared-cache scenarios with sufficient storage, we recommend installing all data eagerly with a single leader process and letting workers use the pre-populated cache without locks via `cache_lock=False`.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
