# TiPToP

This implementation provides functionality for running TiPToP on MolmoSpaces.

TiPToP runs as a separate **remote inference server**: this policy is a thin websocket client that sends each observation (wrist-camera RGB-D, camera intrinsics/extrinsics, current joint positions, and the task description) to the server and executes the returned plan. You must start the TiPToP server before running an evaluation.

For instructions on setting up and running the TiPToP server, see the [TiPToP documentation](https://tiptop-robot.readthedocs.io/en/latest/).

## Installation

```bash
pip install -e .
```

## Running with MolmoSpaces

First, start the TiPToP inference server (defaults to `localhost:8765`). Then run the evaluation:

```bash
python -m molmo_spaces.evaluation.eval_main molmospaces_zoo.tiptop.config:TiptopEvalConfig --benchmark_dir <benchmark_path>
```

To point at a server on a different host/port, edit `remote_config` in
[`TiptopPolicyConfig`](./config.py) (`host`, `port`, `max_retries`).

## Notes

- **Depth:** TiPToP requires depth from the wrist camera. `TiptopPolicyConfig` sets
  `force_enable_depth = True`.
- **Observation pose:** At the start of each trajectory the arm interpolates to
  `cam_obs_qpos` over `cam_obs_n_steps` steps so the wrist camera gets a clear view of the
  scene before the observation is sent to the server. Set `cam_obs_qpos = None` to disable.
