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

# Enabling NVIDIA Flare POC Mode

This part of the How-To assumes you have completed [Part 1: Setting up a basic Data Federation for local testing](01-local-federation.md). You have a working federation with `federation.dfm.yaml`, adapter code in `myfed/myfed/lib/`, a registered federation, generated code, and a notebook that runs with `target="local"`.

Here we add **NVIDIA Flare POC (Proof of Concept) mode** so you can run the same federation over Flare's simulated distributed infrastructure on your machine.

## Table of contents

- [What You will Do](#what-you-will-do)
- [Step 1: Add the Server Site to the Federation (Required for POC)](#step-1-add-the-server-site-to-the-federation-required-for-poc)
- [Step 2: Add the NVIDIA Flare Project File](#step-2-add-the-nvidia-flare-project-file)
- [Step 3: Point DFM at the Project File](#step-3-point-dfm-at-the-project-file)
- [Step 4: Regenerate Code and Reinstall](#step-4-regenerate-code-and-reinstall)
- [Step 5: Start POC](#step-5-start-poc)
- [Step 6: Update Your Notebook for Flare](#step-6-update-your-notebook-for-flare)
- [Step 7: Run the Notebook](#step-7-run-the-notebook)
- [Cleanup](#cleanup)
- [Troubleshooting (POC-specific)](#troubleshooting-poc-specific)
- [Next Steps](#next-steps)

## What You will Do

1. Add a **server** site to `federation.dfm.yaml` (required so DFM generates the server runtime for Flare).
2. Add a **project.yaml** file (Flare's infrastructure descriptor).
3. **Update** your federation registration to point to the project.
4. **Regenerate** federation code and reinstall the package.
5. **Start POC** and run your existing notebook with `target="flare"`.

Your adapter code stays the same. You will add one **server** site to `federation.dfm.yaml` (so the Flare controller can load its runtime module), add `project.yaml`, then change the notebook connection.

---

## Step 1: Add the Server Site to the Federation (Required for POC)

In POC mode, the Flare **server** participant runs the DFM controller, which loads a runtime module for the site named `server`. That module is only generated when `server` is listed under `sites` in your federation config. Part 1 only defines `homesite`, `loader`, and `plotter`, so you must add a `server` site before running POC.

Open `myfed/configs/federation.dfm.yaml` and add a `server` entry under `sites` with an empty interface (the server does not run pipeline operations):

```yaml
sites:
  homesite:
    # ... existing homesite entry unchanged ...

  server:
    info:
      description: "Flare server (controller); no operations"
    interface: {}

  loader:
    # ... existing loader entry unchanged ...
  plotter:
    # ...
```

Then **regenerate code** (you will do this again after adding project.yaml in Step 2, or do it once after Step 2):

```bash
dfm fed gen code myfed --output-dir myfed
```

This creates `myfed/fed/runtime/server/` so the controller can load `myfed.fed.runtime.server`.

---

## Step 2: Add the NVIDIA Flare Project File

Flare needs a **project** file that defines participants (server and clients) and how to build startup kits. DFM uses this for POC and for later provisioning.

### What project.yaml Is For

- **federation.dfm.yaml** defines your *operations and sites* (including the `server` site you added in Step 1, plus loader, plotter, etc.).
- **project.yaml** defines the *Flare infrastructure*: one server, one admin, and one client per *executing* site.

Client names in `project.yaml` must match the site names in `federation.dfm.yaml` (except `homesite` and `server`; the server is the Flare server participant, not a client).

### Create `myfed/configs/project.yaml`

Create `myfed/configs/project.yaml` with the following. Use the same workspace directory as in Part 1 (for example, `~/zero-to-thirty`).

```yaml
api_version: 3

name: myfed
description: "Array subsetting federation"

participants:
  # Admin: required by Flare. Name must be email format; use admin@nvidia.com (DFM default).
  - name: admin@nvidia.com
    type: admin
    org: myorg
    role: project_admin

  # Server: central coordinator. Needs fed_learn_port and admin_port.
  - name: server
    type: server
    org: myorg
    fed_learn_port: 8002
    admin_port: 8003

  # Clients: one per executing site in federation.dfm.yaml (loader, plotter in Part 1).
  - name: loader
    type: client
    org: myorg

  - name: plotter
    type: client
    org: myorg

builders:
  - path: nvflare.lighter.impl.workspace.WorkspaceBuilder
    args:
      template_file:
        - master_template.yml
        - aws_template.yml
        - azure_template.yml
  - path: nvflare.lighter.impl.template.TemplateBuilder
  - path: nvflare.lighter.impl.static_file.StaticFileBuilder
    args:
      config_folder: config
      overseer_agent:
        path: nvflare.ha.dummy_overseer_agent.DummyOverseerAgent
        overseer_exists: false
        args:
          sp_end_point: server:8002:8003
  - path: nvflare.lighter.impl.cert.CertBuilder
  - path: nvflare.lighter.impl.signature.SignatureBuilder
  - path: nv_dfm_core.targets.flare.builder.WorkspaceArchiveBuilder
```

```{important}
If your Part 1 federation has different site names (for example, if you added a `slicer` site), add a matching `- name: slicer` client under `participants` and keep client names in sync with `federation.dfm.yaml`.
```

---

## Step 3: Point DFM at the Project File

Register the project path so DFM (and `dfm poc`) can find it. From your workspace root (for example, `~/zero-to-thirty`):

```bash
dfm fed config set myfed \
  --federation-dir myfed \
  --config-path configs/federation.dfm.yaml \
  --project-path configs/project.yaml
```

If you already had `myfed` registered without a project path, this updates it. Paths are relative to the federation directory: `configs/project.yaml` means `myfed/configs/project.yaml`.

---

## Step 4: Regenerate Code and Reinstall

Because you added the `server` site (and possibly only just added `project.yaml`), regenerate and reinstall so all participants have the right runtime:

```bash
dfm fed gen code myfed --output-dir myfed
pip install -e myfed/
```

---

## Step 5: Start POC

From the workspace root:

```bash
dfm poc start -f myfed
```

Optional: check status and logs:

```bash
dfm poc status -f myfed
dfm poc logs
```

If something goes wrong (for example, port in use or certificate errors), stop and clean up, then try again:

```bash
dfm poc stop
dfm poc cleanup -f myfed
dfm poc start -f myfed
```

---

## Step 6: Update Your Notebook for Flare

Your pipeline and the rest of the notebook stay the same. Only the **connection** cell changes: use `target="flare"` and pass the **admin startup kit** path.

After POC has started, Flare creates the admin startup kit under the workspace, for example:

`workspace/myfed_poc/myfed/prod_00/admin@nvidia.com`

From a notebook under `myfed/apps/`, the workspace root is typically two levels up (for example, `Path.cwd().parent.parent`). Use that to build the path.

**Replace** your existing “Connect to federation” cell with:

```python
from pathlib import Path

# POC creates the admin startup kit here (relative to workspace root).
# If the notebook is in myfed/apps/, workspace root is parent.parent.
admin_startup_kit = (
    Path.cwd().parent.parent
    / "workspace"
    / "myfed_poc"
    / "myfed"
    / "prod_00"
    / "admin@nvidia.com"
)

session = get_session(target="flare", admin_package=admin_startup_kit)
session.connect()
print("Connected to federation!")
```

Keep all other cells as in Part 1 (same pipeline, prepare, execute, callback, wait, display, close). Run the notebook from the workspace (or ensure the path to `admin_startup_kit` is correct for your directory layout).

---

## Step 7: Run the Notebook

1. Start Jupyter from the workspace root:
   ```bash
   cd ~/zero-to-thirty
   jupyter lab
   ```
2. Open `myfed/apps/application.ipynb` (or your notebook).
3. Run all cells in order.

You should see the same behavior as in Part 1, but with jobs running over Flare POC instead of the local target.

**NOTE:** After these changes, you can _still_ run in `local` target mode.  If you change your Cell 2 back to use `get_session(target="local")`, it should still work!

---

## Cleanup

When you are done with POC:

```bash
dfm poc stop
dfm poc cleanup -f myfed
```

---

## Troubleshooting (POC-specific)

| Issue | What to do |
|-------|------------|
| Port already in use / certificate errors | Run `dfm poc stop`, `dfm poc cleanup -f myfed`, then `dfm poc start -f myfed` again. |
| “Startup kit does not exist” | Ensure POC has finished (`dfm poc wait -f myfed`). Fix the `admin_startup_kit` path (workspace root and `workspace/myfed_poc/...`). |
| “Cannot find module myfed” on POC sites | From workspace root: `pip install -e myfed/`. Then restart POC. |
| “Could not locate a Python module for name myfed.fed.runtime.server” | Add the `server` site to `federation.dfm.yaml` (Step 1), then run `dfm fed gen code myfed --output-dir myfed` and `pip install -e myfed/`. Restart POC. |
| Site names in project.yaml | Client names under `participants` must match site names in `federation.dfm.yaml` (for example, `loader`, `plotter`). |

For general federation or pipeline issues, see Part 1.
