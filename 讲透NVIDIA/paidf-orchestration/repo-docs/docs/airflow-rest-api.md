# Run Workflows with the Airflow REST API

Every workflow guide shows how to start a run from the Airflow UI. This page is the equivalent
headless path: authenticate, trigger a DAG with a payload, monitor it, read task logs, and stop it
safely. It works for every DAG this deployment registers, so the per-workflow guides link here
instead of repeating it.

The commands use `curl` and `python3` only. They assume the controller is installed as described in
[Getting Started](getting-started.md) and that `KUBECONFIG` points at the same cluster.

## Reach the API

Use the API server's ClusterIP when the host can route to the cluster service network:

```bash
AIRFLOW_URL="http://$(kubectl get svc -n sdg-workflow sdg-workflow-controller-api-server \
  -o jsonpath='{.spec.clusterIP}'):8080"
curl -s --max-time 8 "$AIRFLOW_URL/api/v2/version"
```

If that request times out, run `make port-forward` in a separate terminal (or as a background job;
it blocks) and use `AIRFLOW_URL=http://localhost:8080` instead.

## Authenticate

Airflow 3 issues a JWT from `/auth/token`. The credentials are the ones in
`airflow.createUserJob.defaultUser` in `deploy/values.yaml` (`admin` / `admin` unless you changed
them):

```bash
RESPONSE=$(curl -s -X POST "$AIRFLOW_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}')

# Keep the token in an owner-only header file so it never appears in the process list.
AUTH_HEADER=$(umask 077; mktemp)
RESPONSE="$RESPONSE" python3 -c \
  'import json, os; print("Authorization: Bearer " + json.loads(os.environ["RESPONSE"])["access_token"])' \
  > "$AUTH_HEADER"
api() { curl -s -H @"$AUTH_HEADER" "$@"; }
```

Every later command calls `api` instead of `curl`, captures the response in `RESPONSE`, and parses
it with `python3`. Tokens expire; if a call returns `401` or `403`, request a new token. Delete
`"$AUTH_HEADER"` when you are done.

## Check the DAG Before Triggering

Pick the DAG ID from the workflow's guide, for example `defect_image_generation_smt_dag_k8s`:

```bash
DAG_ID=defect_image_generation_smt_dag_k8s

# Loaded and unpaused? A 404 means the DAG is not registered in this image.
RESPONSE=$(api "$AIRFLOW_URL/api/v2/dags/$DAG_ID")
RESPONSE="$RESPONSE" python3 -c 'import json, os; d = json.loads(os.environ["RESPONSE"]); print("is_paused:", d.get("is_paused"))'

# A DAG can be missing because its file failed to parse.
RESPONSE=$(api "$AIRFLOW_URL/api/v2/importErrors")
RESPONSE="$RESPONSE" python3 -c 'import json, os; print("import errors:", json.loads(os.environ["RESPONSE"])["total_entries"])'

# Pools and their free slots.
RESPONSE=$(api "$AIRFLOW_URL/api/v2/pools?limit=100")
RESPONSE="$RESPONSE" python3 -c 'import json, os; [print(p["name"], p["open_slots"], "/", p["slots"]) for p in json.loads(os.environ["RESPONSE"])["pools"]]'
```

Connections such as `kubernetes_remote` are injected as environment variables, so
`GET /api/v2/connections/kubernetes_remote` returns `404` on a healthy controller. That is expected.

## Trigger a Run

Each workflow DAG reads its configuration from `conf.payload`. Pass the same JSON you would paste
into the UI's trigger form; the starter files under [`payloads/dev/`](../payloads/dev/) are valid
inputs. Always pass an explicit payload: the DAG defaults point at sample data and endpoints that
are not yours.

The request body must include `logical_date`. The current UTC time is fine for a manual run.

```bash
PAYLOAD_FILE=payloads/dev/defect_image_generation_smt_dag/default_payload.json

BODY=$(python3 - "$PAYLOAD_FILE" <<'PY'
import datetime, json, sys
payload = json.load(open(sys.argv[1]))
print(json.dumps({
    "logical_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "conf": {"payload": payload},
}))
PY
)

RESPONSE=$(api -X POST -H "Content-Type: application/json" \
  "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns" -d "$BODY")
DAG_RUN_ID=$(RESPONSE="$RESPONSE" python3 -c 'import json, os; d = json.loads(os.environ["RESPONSE"]); print(d.get("dag_run_id") or d)')
echo "$DAG_RUN_ID"
```

A `422` response means the request body was malformed. A payload that is well-formed JSON but
invalid for the workflow is accepted here and then fails in the run's `validate_payload` task.

## Monitor a Run

Poll the run state until it is `success` or `failed`:

```bash
while :; do
  RESPONSE=$(api "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns/$DAG_RUN_ID")
  STATE=$(RESPONSE="$RESPONSE" python3 -c 'import json, os; print(json.loads(os.environ["RESPONSE"])["state"])')
  echo "$(date -u +%H:%M:%S) $STATE"
  case "$STATE" in success|failed) break ;; esac
  sleep 60
done
```

List task states to see where a run is, or which task failed:

```bash
RESPONSE=$(api "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns/$DAG_RUN_ID/taskInstances?limit=200")
RESPONSE="$RESPONSE" python3 -c '
import json, os
for t in json.loads(os.environ["RESPONSE"])["task_instances"]:
    print(str(t["state"]).ljust(15), t["task_id"], t["map_index"])
'
```

`skipped` is normal for branches that do not apply, such as service startup in external mode.
`up_for_retry` means the task failed and has retries left; wait before diagnosing it.

## Read Task Logs

```bash
TASK_ID=validate_payload   # group-qualified, e.g. cosmos_augmentation.augmentation_external
TRY=1                      # try_number starts at 1
MAP_INDEX=-1               # -1 for unmapped tasks; 0, 1, ... for mapped tasks
RESPONSE=$(api "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns/$DAG_RUN_ID/taskInstances/$TASK_ID/logs/$TRY?map_index=$MAP_INDEX")
RESPONSE="$RESPONSE" python3 -c '
import json, os
content = json.loads(os.environ["RESPONSE"]).get("content", "")
if isinstance(content, list):
    for entry in content:
        print(entry.get("event", entry) if isinstance(entry, dict) else entry)
else:
    print(content)
'
```

## Stop a Run

Do not delete the DAG run. Deleting it skips the shutdown tasks and leaves GPU Deployments,
Services, and pods running in `sdg-workflow`. This is the API form of
[Stop a Running Workflow](getting-started.md#stop-a-running-workflow-and-clean-up-kubernetes-resources).

1. Mark each **running task** failed, not the DAG run. The run then proceeds to `fail_pipeline` and
   service shutdown. Mapped tasks are addressed with their map index in the path:

   ```bash
   RESPONSE=$(api "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns/$DAG_RUN_ID/taskInstances?state=running&limit=200")
   RUNNING=$(RESPONSE="$RESPONSE" python3 -c '
   import json, os
   for t in json.loads(os.environ["RESPONSE"])["task_instances"]:
       print(t["task_id"] + ("" if t["map_index"] < 0 else "/" + str(t["map_index"])))
   ')

   for TI in $RUNNING; do
     api -X PATCH -H "Content-Type: application/json" \
       "$AIRFLOW_URL/api/v2/dags/$DAG_ID/dagRuns/$DAG_RUN_ID/taskInstances/$TI" \
       -d '{"new_state": "failed"}' >/dev/null && echo "marked failed: $TI"
   done
   ```

2. When the run reaches `failed`, its failure callback queues `k8s_resource_cleanup_dag` for this
   run. If services are still up after that, trigger the cleanup yourself, scoped to this run:

   ```bash
   api -X POST -H "Content-Type: application/json" \
     "$AIRFLOW_URL/api/v2/dags/k8s_resource_cleanup_dag/dagRuns" \
     -d "{\"logical_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"conf\": {\"target_run_id\": \"$DAG_RUN_ID\"}}"
   ```

   Always set `target_run_id`. An empty value deletes every k8s-plugin resource in the namespace,
   including other users' runs.

## Common Errors

| Response | Cause | Fix |
| --- | --- | --- |
| `401` or `403` | Token missing, invalid, or expired | Request a new token |
| `404` on `/api/v2/dags/$DAG_ID` | DAG not in the deployed image, or its manifest is missing | Check `importErrors`; rebuild with `make build sdg-controller` and reinstall |
| `422` with `"loc": ["body", "logical_date"]` | `logical_date` omitted from the trigger body | Add `logical_date` as shown above |
| `409` on trigger | A run with the same `dag_run_id` already exists | Read back the existing run and compare `conf.payload` with the intended payload. If it matches, monitor that run. Choose a new ID only for an intentional new run or a confirmed collision with a different request. |
| Run stays `queued` | No open slots in a pool the run needs | Check pool slots above and free capacity |
