<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Setting up a basic Data Federation for local testing

In this part of the How-To, we will show how to create your first Data Federation and run it locally, distributing different sites across different processes on your local machine.

## Table of contents

- [Prerequisites](#prerequisites)
- [Step 1: Create Workspace and Install DFM](#step-1-create-workspace-and-install-dfm)
- [Step 2: Create Federation Structure](#step-2-create-federation-structure)
- [Step 3: Write the Federation Configuration File](#step-3-write-the-federation-configuration-file)
- [Step 4: Create Adapter Implementations](#step-4-create-adapter-implementations)
- [Step 5: Register and Generate Federation Code](#step-5-register-and-generate-federation-code)
- [Step 6: Create a Jupyter Notebook for testing](#step-6-create-a-jupyter-notebook-for-testing)
- [Step 7: Run Your Notebook](#step-7-run-your-notebook)
- [Understanding What Happened](#understanding-what-happened)
- [Customizing the Pipeline](#customizing-the-pipeline)
- [Cleanup](#cleanup)
- [Next Steps](#next-steps)

## Prerequisites

Before starting this guide, you need:

1. **Python 3.10 or higher**: Installed on your system (check with `python --version`) along with `pip` and `venv`
2. **Basic Python Knowledge**: Familiarity with Python, async functions, and virtual environments
3. **Your Code**: The `plot_gradient.py` file with the three functions described above

## Step 1: Create Workspace and Install DFM

### Create a Workspace Directory

Create a directory for your federation project and navigate into that new directory:

```bash
mkdir -p ~/zero-to-thirty
cd ~/zero-to-thirty
```

### Create a Virtual Environment

Create a virtual environment inside your workspace directory:

```bash
python -m venv .venv
```

```{note}
Make sure you have Python 3.10 or higher installed with `pip` and `venv`.
```

### Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### Install the DFM core package and dependencies

```bash
pip install nv-dfm-core pillow
```

This installs the DFM core framework and all required dependencies.

### Verify Installation

Check that DFM is available:

```bash
dfm --version
dfm --help
```

You should see the DFM CLI help output with commands like `fed`, `poc`, `dev`, etc.

```{important}
Keep the virtual environment activated for all subsequent commands in this guide. If you close your terminal and come back later, remember to:
1. Navigate to your workspace: `cd ~/zero-to-thirty`
2. Reactivate the environment: `source .venv/bin/activate`
```

## Step 2: Create Federation Structure

Create a directory called `myfed` for your federation in your workspace:

```bash
mkdir -p myfed/apps
mkdir -p myfed/configs
mkdir -p myfed/myfed/lib
```

Through the course of this tutorial, you will create the following content:

```
myfed/
├── apps/
│   └── application.ipynb       # We'll create this
├── configs/
│   └── federation.dfm.yaml     # We'll create this
└── myfed/
    ├── setup.py                # We'll create this
    └── lib/
        ├── __init__.py         # We'll create this
        ├── create.py           # We'll create this
        ├── subset.py           # We'll create this
        └── plot2d.py           # We'll create this
```

## Step 3: Write the Federation Configuration File

The federation configuration file (`federation.dfm.yaml`) is the heart of your DFM setup. It defines the DFM schema version, federation info, operations, and sites. Let's build it step by step.

Create `myfed/configs/federation.dfm.yaml` and we'll fill it in section by section.

### DFM Schema Version

Start with the DFM schema version:

```yaml
dfm: 1.0.0
```

**Parameter:**
- **`dfm`**: DFM configuration schema version (currently `1.0.0`)

### Federation Info

The `info` section provides metadata about your federation:

```yaml
info:
  api-version: 0.0.1
  code-package: myfed
  description: "Distributed array subsetting and plotting"
```

**Parameters:**
- **`api-version`**: Your federation's API version in X.Y.Z format (for example, `0.0.1`)
- **`code-package`**: Python package name for generated code (must match your directory name)
- **`description`**: Human-readable description of what this federation does

This section tells DFM how to generate code and identifies your federation's version.

### Operations

The `operations` section defines the API for your federation—what operations can be called, what parameters they accept, and what they return.

Each operation is defined with a hierarchical name (for example, `array.Create`), which creates a namespace for organizing related operations.

#### Define the Create Operation:

```yaml
operations:
  array.Create:
    description: "Create a gradient array"
    parameters:
      shape:
        type: array
        description: "Shape of the array to create"
      min:
        type: number
        description: "Minimum value in the array"
      max:
        type: number
        description: "Maximum value in the array"
    required:
      - shape
    returns: object
```

**Structure:**
- **Operation name** (`array.Create`): Hierarchical name (namespace.OperationName)
- **`description`**: Plain text describing what this operation does
- **`parameters`**: Dictionary of input parameters (empty `{}` means no parameters).  Each parameter is defined by:
  - **`type`**: The type of the parameter as a string (supports `string`, `number`, `integer`, `boolean`, `array`, and `object`)
  - **`description`**: Human-readable description of the parameter
- **`required`**: List of required parameter names (empty `[]` if there are no required parameters)
- **`returns`**: Return type as a string

```{note}
The `object` type represents a generic Python object which will be Pickled when sent between DFM sites, and the `array` type represents a Python `list` (not a tuple!).
```

#### Define the Subset Operation:

```yaml
  array.Subset:
    description: "Extract slice from array"
    parameters:
      array:
        type: object
        description: "Input array"
      index:
        type: array
        description: "Index specification (list of integers)"
    required:
      - array
      - index
    returns: object
```

**Key difference**: This operation has **parameters**:
- **`array`**: Input parameter (type `object` for complex Python objects like `ndarray`)
- **`index`**: Input parameter (type `array` for list of `int` indices)

Each parameter has:
- **`type`**: Type hint (`object`, `string`, `integer`, `number`, `boolean`, `array`)
- **`description`**: What this parameter is for

#### Define Plot2D Operation:

```yaml
  array.Plot2D:
    description: "Convert 2D array to grayscale image"
    parameters:
      array:
        type: object
        description: "2D array to plot"
    required:
      - array
    returns: object
```

#### How Operations Map to Adapters

```{important}
The operation definition in the config file directly maps to your adapter class structure.
```
1. **`parameters`** → Arguments to the adapter's `body()` method
   - Each parameter name becomes a keyword argument to `body()`
   - Example: `array.Subset` has parameters `array` and `index`, so its adapter's `body()` will be:
     ```python
     async def body(self, array: np.ndarray, index: list) -> np.ndarray:
     ```

2. **`returns`** → Return value of the adapter's `body()` method
   - The adapter's `body()` must return a value compatible with the configured return type
   - Example: `array.Create` should return:
     ```python
     return array
     ```
   - The returned value can be passed directly to downstream operations in a pipeline

3. **Site `args`** (defined in sites section) → Maps values to the adapter's `body()` method arguments
   - Every adapter receives `site: Site` and `provider: Provider | None` to its `__init__()` automatically
   - The `args` section maps operation parameters and other values to `body()` arguments using `from-param`, `const`, etc.
   - If an operation has no parameters, `args` can be empty (`{}`)

We'll see this mapping in action when we create the adapters in Step 4.

### Sites

The `sites` section defines:
1. What sites exist in your federation
2. Which operations each site can execute
3. How operations map to your adapter implementations
4. How to pass arguments to adapters

Each site has an `info` subsection and an `interface` subsection.

#### Define Homesite:

```yaml
sites:
  homesite:
    info:
      description: "User's notebook/application site"
    interface: {}
```

**Special site**: Every federation needs a `homesite` where your application runs (your Jupyter notebook, in this example). It typically has an empty interface because it doesn't execute operations—it just sends work to other sites and receives results.

**Structure:**
- **Site name** (`homesite`): Special reserved name for the application site
- **`info`**: Metadata about the site
  - **`description`**: What this site does
- **`interface`**: Maps operations to adapters (empty for homesite)

#### Define Loader Site:

Now, we will define the `loader` site, where the arrays are created and sliced.  On this site, we co-locate the `array.Create` operation and the `array.Subset` operation because the initial array may be too large to communicate.  But communicating a _subset_ of the original array may be more manageable.  Thus, we can string together `array.Create` and `array.Subset` operations and ensure that both operations will be done on the same site, preventing communication of the large array.

```yaml
  loader:
    info:
      description: "Site where arrays are constructed and sliced"
    interface:
      "#/operations/array.Create":
        adapter: myfed.lib.Create
        args:
          shape:
            from-param: shape
          min:
            const: -100.0
            expose-as:
              param: min
              type: number
              description: "Minimum value in the array"
          max:
            const: 100.0
            expose-as:
              param: max
              type: number
              description: "Maximum value in the array"
      "#/operations/array.Subset":
        adapter: myfed.lib.Subset
        args:
          array:
            from-param: array
          index:
            from-param: index
```

**Structure:**
- **Site name** (`loader`): Arbitrary name for this site
- **`info`**: Metadata
- **`interface`**: Maps operations to adapters
  - **Key** (`"#/operations/array.Create"`): JSON pointer reference to operation
    - Format: `"#/operations/<operation-name>"`
    - The `#` refers to the root of the config file
    - **`adapter`**: Full Python path to adapter class
      - Format: `<package>.lib.<ClassName>` or `<package>.lib.<module>.<ClassName>`
      - Example: `myfed.lib.Create`
    - **`args`**: The `args` section maps operation parameters to the adapter's `body()` method arguments:
      - **`from-param`**: Pass the operation parameter directly to the corresponding `body()` argument
      - **`const`**: Pass the given constant value to the `body()` argument
      - **`expose-as`**: Allow the user to override the `const` value 
        - **`param`**: The operation parameter to map to the adapter's `body()` method argument
        - **`type`**: The parameter type
        - **`description`**: Human-readable description of the parameter

#### Define Plotter Site:

```yaml
  plotter:
    info:
      description: "Site for visualization"
    interface:
      "#/operations/array.Plot2D":
        adapter: myfed.lib.Plot2D
        args:
          array:
            from-param: array
```

Same pattern - `args` maps the `array` parameter from the operation to the adapter's `body()` method.

### Complete Configuration File

Putting it all together, your complete `myfed/configs/federation.dfm.yaml` should look like:

```yaml
dfm: 1.0.0

info:
  api-version: 0.0.1
  code-package: myfed
  description: "Distributed array subsetting and plotting"

operations:
  array.Create:
    description: "Create a gradient array"
    parameters:
      shape:
        type: array
        description: "Shape of the array to create"
      min:
        type: number
        description: "Minimum value in the array"
      max:
        type: number
        description: "Maximum value in the array"
    required:
      - shape
    returns: object

  array.Subset:
    description: "Extract slice from array"
    parameters:
      array:
        type: object
        description: "Input array"
      index:
        type: array
        description: "Index specification (list of integers)"
    required:
      - array
      - index
    returns: object

  array.Plot2D:
    description: "Convert 2D array to grayscale image"
    parameters:
      array:
        type: object
        description: "2D array to plot"
    required:
      - array
    returns: object

sites:
  homesite:
    info:
      description: "User's notebook/application site"
    interface: {}

  loader:
    info:
      description: "Site where arrays are constructed and sliced"
    interface:
      "#/operations/array.Create":
        adapter: myfed.lib.Create
        args:
          shape:
            from-param: shape
          min:
            const: -100.0
            expose-as:
              param: min
              type: number
              description: "Minimum value in the array"
          max:
            const: 100.0
            expose-as:
              param: max
              type: number
              description: "Maximum value in the array"
      "#/operations/array.Subset":
        adapter: myfed.lib.Subset
        args:
          array:
            from-param: array
          index:
            from-param: index

  plotter:
    info:
      description: "Site for visualization"
    interface:
      "#/operations/array.Plot2D":
        adapter: myfed.lib.Plot2D
        args:
          array:
            from-param: array
```

### Understanding the Flow

When you write a pipeline:

```python
result = Create(site="loader")
```

The DFM uses this configuration to:
1. Look up the `array.Create` operation definition (parameters and returns)
2. Find which site implements it (`loader` in `sites` section via `"#/operations/array.Create"`)
3. Find the adapter class (`myfed.lib.Create`)
4. Map any arguments using the `args` section (with `from-param`, `const`, etc.)
5. Generate code that calls that adapter at runtime

This configuration file is the "contract" between your application code and the distributed execution. The JSON pointer syntax (`"#/operations/..."`) explicitly links interface implementations to operation definitions.

## Step 4: Create Adapter Implementations

Now wrap your original functions in the `body()` method of DFM adapter classes. Remember the mapping from Step 4:
- **`parameters`** in the config → define what arguments the `body()` method accepts
- **`returns`** in the config → dictionary returned by `body()` method  
- **`args`** in the config → maps operation parameters (and other values) to `body()` method arguments using `from-param`, `const`, etc.

Each adapter class must have:
1. An `__init__(self, site: Site, provider: Provider | None)` method (receives site context)
2. An `async def body(self, **params)` method where `**params` are the arguments mapped from the config's `args` section

### Create `myfed/myfed/lib/create.py`:

```python
import numpy as np
from pathlib import Path
from nv_dfm_core.exec import Site, Provider

class Create:
    """Adapter for creating 3D gradient arrays."""

    def __init__(self, site: Site, provider: Provider | None):
        self._site = site

    async def body(self, shape: tuple[int, ...], min: float = 0.0, max: float = 1.0) -> np.ndarray:
        ndims = len(shape)
        grads = [np.arange(s) for s in shape]
        grad = sum(g[tuple(slice(None) if i == j else np.newaxis for i in range(ndims))] / (shape[j] - 1) for j, g in enumerate(grads)) / ndims
        return np.asarray((max - min) * grad + min)
```

### Create `myfed/myfed/lib/subset.py`:

```python
import numpy as np
from nv_dfm_core.exec import Site, Provider

class Subset:
    """Adapter for subsetting arrays."""

    def __init__(self, site: Site, provider: Provider | None):
        self._site = site

    async def body(self, array: np.ndarray, index: list) -> np.ndarray:
        return array[tuple(index)]
```

### Create `myfed/myfed/lib/plot2d.py`:

```python
import numpy as np
from PIL import Image
from nv_dfm_core.exec import Site, Provider

class Plot2D:
    """Adapter for plotting 2D arrays."""

    def __init__(self, site: Site, provider: Provider | None):
        self._site = site

    async def body(self, array: np.ndarray):
        if len(np.shape(array)) != 2:
            raise ValueError("Array must be 2D to be plotted")

        normalized = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)
        return Image.fromarray(normalized, mode='L')
```

### Create `myfed/myfed/lib/__init__.py`:

Finally, to make the `myfed/myfed/lib` subdirectory an importable package, we need to create the `__init__.py` file:

```python
from .create import Create
from .subset import Subset
from .plot2d import Plot2D

__all__ = ["Create", "Subset", "Plot2D"]
```

## Step 5: Register and Generate Federation Code

Before generating code for your federation, you need to register your federation with DFM so it knows where to find the configuration files.

### Create Federation Registry (First Time Only)

If this is your first time using DFM, create an empty federation registry file:

```bash
# From your workspace directory (~/zero-to-thirty)
dfm fed config create-default
```

This creates a `federations.yaml` file that will track all your registered federations. The file location defaults to `federations.yaml` in the workspace directory.

```{note}
- You only need to run this command once per workspace
- The file is initially empty — you'll add your federation configurations in the next step
- If you already have a `federations.yaml` file, skip this step
```

### Register the Federation

From your workspace directory, register your federation:

```bash
# Make sure you're in the workspace root (where federations.yaml exists)
cd ~/zero-to-thirty
dfm fed config set myfed \
  --federation-dir myfed \
  --config-path configs/federation.dfm.yaml \
  --project-path None
```

**NOTE:** At the moment, you need to supply a `--project-path` even though we do not need it for `local` execution.  Since we are not providing any NVFlare project configuration for our `local` setup, we can just supply `None`.

**Parameters:**
- `myfed` - The federation name (must match `code_pkg_name` in your config)
- `--federation-dir myfed` - The federation root directory (relative to workspace root)
- `--config-path configs/federation.dfm.yaml` - Path to your federation config file (**relative to the federation directory**, not the workspace)
- `--project-path None` - Path to the NVFlare project configuration file, which we don't need so we supply `None`.

**Important Path Resolution**:
- `--federation-dir` is relative to the workspace root directory (where `federations.yaml` exists)
- `--config-path` is relative to the `--federation-dir` path
- Example: With `--federation-dir myfed` and `--config-path configs/federation.dfm.yaml`, the final path will be `myfed/configs/federation.dfm.yaml`

This adds your federation to the `federations.yaml` registry file, which tracks all your federation configurations.

### Generate Federation Code

Now that your federation `myfed` is registered, generate the DFM runtime code from your configuration:

```bash
# Still in the workspace root directory
dfm fed gen code myfed --output-dir myfed
```

This creates:
- `myfed/myfed/fed/api/` - Operation classes (`array.py` with `Create`, `Subset`, `Plot2D`)
- `myfed/myfed/fed/site/` - Site-specific APIs
- `myfed/myfed/fed/runtime/` - Runtime execution code for each site

You should see output confirming the code generation completed successfully.

**Notes**:
- The `--output-dir myfed` tells DFM to generate code inside the `myfed/myfed` directory, as this output directory is relative to the `federation_dir` in the `myfed` section of your `federations.yaml` file (created with the `dfm fed config create-default` command above)
- You may see warnings like "Compute cost not set for operation... Using suboptimal default values" - these are informational warnings about optimization settings and can be safely ignored for now. Compute costs are optional metadata used by DFM's optimizer to make scheduling decisions, but they're not required for basic pipeline execution.

### Install the Generated Code as a Package

```{important}
You must install the generated `myfed` code as a Python package so that local target execution can import `myfed.fed.runtime.*` modules. Skipping this step will cause import errors when running the pipeline.
```

The `myfed/myfed` directory in your workspace needs to be an installable package so that individual sites can import the federation code directly. To do this, we provide a simple `setup.py` script in the `myfed/` directory and install it into our workspace environment (so we can use it directly in our notebook).

```bash
# From the workspace root (~/zero-to-thirty)

# Create a setup.py to handle the package structure
cat > myfed/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="myfed",
    version="0.1.0",
    packages=find_packages(where="."),
    install_requires=[
        "nv-dfm-core",
        "numpy",
        "pillow",
    ],
)
EOF

# Install myfed in editable mode
pip install -e myfed/
```

This installs the `myfed` package so local target workers can import `myfed.fed.runtime.*` modules.

## Step 6: Create a Jupyter Notebook for testing

Next, we want to create a Jupyter Notebook were we can create and submit DFM pipelines using the distributed functions we've just created.

First, install JupyterLab if you haven't already:

```bash
pip install jupyterlab
```

Then launch JupyterLab from the workspace root directory:

```bash
cd ~/zero-to-thirty
jupyter lab
```

Create a new notebook at `myfed/apps/application.ipynb` (following the same structure as the example federation).

Add the following cells to your notebook:

### Cell 1: Setup imports

```python
from pathlib import Path

# Import from myfed package (installed via pip install -e myfed/)
from myfed.fed.runtime.homesite import get_session
from myfed.fed.api.array import Create, Subset, Plot2D
from nv_dfm_core.api import Pipeline, Yield, PlaceParam
from nv_dfm_core.session import JobStatus
```

### Cell 2: Connect to federation

```python
session = get_session(target="local")
session.connect()
print("Connected to local federation!")
```

### Cell 3: Define a pipeline

```python
with Pipeline() as p:
    # Tell the loader site to create a 200x300x400 array with values ranging from -500 to 500
    array = Create(site="loader", shape=(200,300,400), min=-500, max=500)
    
    # Tell the loader site to subset that array to get a 2D slice
    array0 = Subset(site="loader", array=array, index=[0])
    
    # Plot at plotter site (array0 will be sent to plotter)
    image = Plot2D(site="plotter", array=array0)
    
    # Return image to notebook
    Yield(value=image)
```

### Cell 4: Prepare the pipeline

```python
prepared = session.prepare(p)
print("Pipeline prepared!")
```

### Cell 5: Execute the pipeline and collect results

```{note}
The callback receives **all data sent to the homesite**, including:
- Yielded results from `Yield` operations
- `StopToken` (indicating pipeline completion)
- Status/error tokens

This means you'll see multiple "CALLBACK CALLED" messages (typically 3), but only the actual yielded data is added to the `results` list.
```

```python
results = []

def collect_result(from_site, from_node, frame, target_place, data):
    from nv_dfm_core.api import StopToken, ErrorToken
    
    print(f"CALLBACK CALLED: from_site={from_site}, target_place={target_place}, data type={type(data)}")
    
    # Only collect actual yielded results, not control tokens
    if not isinstance(data, (StopToken, ErrorToken)):
        results.append(data)

print("Submitting job...")
job = session.execute(
    prepared,
    input_params={},
    default_callback=collect_result
)
print(f"Job submitted: {job.job_id}")
```

### Cell 6: Wait for completion and check status

```python
success = job.wait_until_finished(timeout=60.0)  # 60 second timeout
status = job.get_status()
print(f"Job completed: {success}")
print(f"Job status: {status}")

# If job failed, there might be errors to check
if status != JobStatus.FINISHED:
    print(f"WARNING: Job did not finish successfully. Check local worker logs printed in the notebook/terminal")
```

### Cell 7: Display the image

```python
if results:
    result_image = results[0]  # Get the image from results
    display(result_image)
else:
    print("No results received")
```

### Cell 8: Cleanup (optional)

```python
session.close()
```

## Step 7: Run Your Notebook

1. Start Jupyter from the myfed directory:

   ```bash
   cd myfed/apps
   jupyter lab
   ```

2. Run all cells in sequence

3. You should see:
   - Connection confirmation
   - Pipeline preparation confirmation  
   - Progress messages during execution
   - The grayscale image displayed in the notebook

## Understanding What Happened

1. **Create** executed on the `loader` site:
   - Constructed a gradient 3D array
   - Sent the 3D array as a token to the next operation

2. **Subset** executed on the `loader` site:
   - Received the 3D array token
   - Extracted slice `[0, :, :]` (first 2D slice)
   - Sent the 2D array as a token to the next operation

3. **Plot2D** executed on the `plotter` site:
   - Received the 2D array token
   - Converted to grayscale PIL Image
   - Sent the image back to homesite

4. **Yield** routed the result to your notebook:
   - Image received via callback
   - Displayed in Jupyter

## Customizing the Pipeline

In your notebook, try changing this basic setup.

### Try extracting a different slice:

```python
# Extract a different slice along axis 0
array_slice = Subset(site="loader", array=array, index=[5])
```

## Cleanup

When done, you can shutdown your Jupyter Lab server (`CTRL-C`) and then `deactivate` your environment.

## Next Steps

- **Flare Variant**: See [02-flare-poc-mode.md](02-flare-poc-mode.md) for distributed Flare/POC execution.
