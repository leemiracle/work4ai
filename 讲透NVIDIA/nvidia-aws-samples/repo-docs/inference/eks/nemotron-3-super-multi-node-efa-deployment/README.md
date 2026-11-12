# Nemotron 3 Super on Amazon EKS with vLLM (multi-node + EFA)

End-to-end guide for deploying [nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16) across **two `g5.48xlarge` nodes** on Amazon EKS, using EFA for inter-node traffic, [LeaderWorkerSet](https://github.com/kubernetes-sigs/lws) + Ray for the multi-pod topology, and the AWS Deep Learning Container (DLC) for vLLM.

For the simpler single-node Nemotron 3 Nano deployment, see [../nemotron-3-nano-single-node-deployment/README.md](../nemotron-3-nano-single-node-deployment/README.md).

## Architecture

```
                        ┌──── EKS cluster (1.31) ────────────────────────────────┐
                        │                                                        │
                        │   LeaderWorkerSet "vllm-nemotron-super" (size: 2)      │
                        │                                                        │
                        │   ┌────────────────── leader ──────────────────────┐   │
                        │   │ g5.48xlarge #1 (8× A10G)                       │   │
                        │   │  ray start --head + vllm OpenAI server         │   │
                        │   │  TP rank group within node, PP stage 0         │   │
                        │   │  vpc.amazonaws.com/efa: 1                      │   │
                        │   └────────────────────────────────────────────────┘   │
                        │                       │                                │
                        │                       ▼  EFA / NCCL (PP activations)   │
                        │   ┌────────────────── worker ──────────────────────┐   │
                        │   │ g5.48xlarge #2 (8× A10G)                       │   │
                        │   │  ray start --address=$LWS_LEADER_ADDRESS:6379  │   │
                        │   │  TP rank group within node, PP stage 1         │   │
                        │   │  vpc.amazonaws.com/efa: 1                      │   │
                        │   └────────────────────────────────────────────────┘   │
                        │                                                        │
                        │   Service "vllm-nemotron-super-api" (ClusterIP, 8000)  │
                        │     selector: role=leader  (workers are Ray-only)      │
                        └────────────────────────────────────────────────────────┘
                                            ▲
                                            │ kubectl port-forward 8000:8000
                                            │
                                       localhost:8000

  Mountpoint S3 CSI ──▶ s3://$S3_BUCKET/nemotron-3-super-bf16/  (ReadOnlyMany)
                          ├── *.safetensors
                          ├── tokenizer.json
                          ├── super_v3_reasoning_parser.py
                          └── …
```

**TP=8 within each node, PP=2 across nodes.** TP all-reduces stay on PCIe inside each node; PP activations cross EFA. Ray is the distributed executor; LeaderWorkerSet coordinates the two pods.

## Why BF16 on g5.48xlarge

| Variant             | Total weights | Per-GPU @ TP=8 PP=2 | Status on A10G (sm_86)                                  |
| ------------------- | ------------- | ------------------- | ------------------------------------------------------- |
| **BF16 (`...-BF16`)** | **247 GB**  | **15.4 GB**         | **~7 GB headroom — tight but works with the tuning in Step 6** |
| FP8 (`...-FP8`)     | 128 GB        | —                   | won't load — vLLM's modelopt-FP8 path requires sm_89+ |
| NVFP4 (`...-NVFP4`) | 80 GB         | —                   | won't load — requires Blackwell sm_100                  |

For roomier headroom without quantization, scale to **TP=8 PP=4 on 4× g5.48xlarge** — see [Next steps](#next-steps).

## Why LeaderWorkerSet

LWS auto-creates the headless Service, injects `LWS_LEADER_ADDRESS` into worker pods, and provides group-restart semantics (`RecreateGroupOnPodRestart`) so a single pod crash recreates the whole group rather than leaving a half-dead Ray cluster. Alternatives: StatefulSet + headless Service (vanilla K8s, more glue), KubeRay (heavier, unlocks Ray Serve), NVIDIA Dynamo (disaggregated prefill/decode — separate sample).

## Prerequisites

- Same baseline as the [nano guide](../nemotron-3-nano-single-node-deployment/README.md): AWS CLI v2, eksctl ≥ 0.190, kubectl ≥ 1.31, HF account + `HF_TOKEN` set, the `hf` CLI (`pip install -U huggingface_hub`)
- ~260 GB of free local disk to stage the BF16 checkpoint, or a Linux EC2 box you can run the staging step from
- **Helm ≥ 3.12** (for the LeaderWorkerSet install)
- Service-quota headroom: you need **≥ 384 vCPU on `g5.48xlarge`** in your target region (192 vCPU × 2 nodes), single AZ. Request via [Service Quotas console](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas) → "Running On-Demand G and VT instances"

```bash
export AWS_REGION=us-east-2
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CLUSTER_NAME=nemotron-super
export S3_BUCKET=nemotron-super-models-${AWS_ACCOUNT_ID}-${AWS_REGION}
export EFA_AZ=us-east-2c   # override if g5.48xlarge capacity is tight in this AZ
```

## Step 1 — Create the S3 bucket and IAM policy

```bash
aws s3 mb s3://$S3_BUCKET --region $AWS_REGION

# Enforce TLS on every bucket request — denies any non-HTTPS access.
aws s3api put-bucket-policy \
  --bucket $S3_BUCKET \
  --policy "$(cat <<EOF
{
  "Version": "2012-10-17",
  "Id": "AllowSSLRequestOnlyPolicy",
  "Statement": [{
    "Sid": "AllowSSLRequestsOnly",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::${S3_BUCKET}",
      "arn:aws:s3:::${S3_BUCKET}/*"
    ],
    "Condition": {
      "Bool": {"aws:SecureTransport": "false"}
    }
  }]
}
EOF
)"

aws iam create-policy \
  --policy-name MountpointS3-${CLUSTER_NAME} \
  --policy-document "$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
    "Resource": [
      "arn:aws:s3:::${S3_BUCKET}",
      "arn:aws:s3:::${S3_BUCKET}/*"
    ]
  }]
}
EOF
)"
```

## Step 2 — Create the EKS cluster with EFA

[manifests/cluster.yaml](manifests/cluster.yaml) provisions a 1.31 control plane, a 2-node managed node group of `g5.48xlarge` (single-AZ, `efaEnabled: true`, `privateNetworking: true`, 500 GiB gp3 root), and the `eks-pod-identity-agent` + `aws-mountpoint-s3-csi-driver` addons. eksctl picks the EKS GPU AMI, installs `aws-efa-installer`, and adds the EFA security-group rules. Because the node group sets `efaEnabled: true`, eksctl also auto-deploys both the NVIDIA device plugin and the EFA device plugin DaemonSets — no manual install needed.

Two ways to apply, same config file:

```bash
# Option A — one command, everything together
envsubst < manifests/cluster.yaml | eksctl create cluster -f -

# Option B — split: cluster first, nodegroup second (lets you recreate only the nodegroup later)
envsubst < manifests/cluster.yaml | eksctl create cluster -f - --without-nodegroup
envsubst < manifests/cluster.yaml | eksctl create nodegroup -f -
```

Verify:

```bash
kubectl describe node -l node.kubernetes.io/instance-type=g5.48xlarge | grep -E 'nvidia.com/gpu|efa'
# Capacity:  nvidia.com/gpu: 8     vpc.amazonaws.com/efa: 1
```

## Step 3 — Install LeaderWorkerSet

```bash
helm install lws oci://registry.k8s.io/lws/charts/lws \
  --version=0.6.1 --namespace lws-system --create-namespace

kubectl rollout status -n lws-system deployment/lws-controller-manager --timeout=180s
```

## Step 4 — Stage the BF16 model files to S3

The BF16 checkpoint is ~247 GB across 50 safetensors shards, plus the `super_v3_reasoning_parser.py` plugin file vLLM needs.

```bash
hf download nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16 \
  --local-dir ./nemotron-3-super-bf16

aws s3 sync ./nemotron-3-super-bf16/ s3://$S3_BUCKET/nemotron-3-super-bf16/
```

If the HF Xet backend throws 504s, re-run (idempotent) or prepend `HF_HUB_DISABLE_XET=1` to fall back to LFS.

## Step 5 — Bind the bucket as a `ReadOnlyMany` PV

[manifests/s3-storage.yaml](manifests/s3-storage.yaml) wires `s3.csi.aws.com` to `$S3_BUCKET` as a `ReadOnlyMany` PV/PVC, which lets both pods mount it concurrently.

```bash
envsubst < manifests/s3-storage.yaml | kubectl apply -f -
```

## Step 6 — Deploy vLLM as a LeaderWorkerSet

[manifests/lws.yaml](manifests/lws.yaml) defines a 2-pod group sharing one Ray cluster: the **leader** runs `ray start --head` then `vllm.entrypoints.openai.api_server` with `--tensor-parallel-size=8 --pipeline-parallel-size=2 --distributed-executor-backend=ray`; the **worker** runs `ray start --address=...:6379 --block` and contributes its 8 GPUs. Both pods get `nvidia.com/gpu: 8` + `vpc.amazonaws.com/efa: 1`, run privileged with `IPC_LOCK` (required for EFA RDMA), a 30 GiB tmpfs `/dev/shm`, and the S3 PVC read-only at `/workspace/models`.

Memory tuning for BF16 (see [Why BF16](#why-bf16-on-g548xlarge)): `--gpu-memory-utilization=0.92`, `--max-model-len=8192`, `--max-num-seqs=4`. Raise these once you confirm a stable boot.

Apply:

```bash
envsubst '$AWS_REGION' < manifests/lws.yaml | kubectl apply -f -
kubectl apply -f manifests/service.yaml
```

First boot streams weights from S3, bootstraps Ray, negotiates NCCL/EFA, and captures CUDA graphs — ~10–15 min:

```bash
kubectl get pods -l app=vllm-nemotron-super -w
kubectl logs -f vllm-nemotron-super-0
```

You're ready when the leader logs show:

```
INFO ...  Initializing a V1 LLM engine ... pipeline_parallel_size=2, tensor_parallel_size=8
INFO ...  Application startup complete.
INFO ...  Uvicorn running on http://0.0.0.0:8000
```

## Step 7 — Connect from your laptop via port-forward

```bash
kubectl port-forward svc/vllm-nemotron-super-api 8000:8000
```

OpenAI-compatible API on `http://localhost:8000/v1`; use `model: "nemotron-super"`:

```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "nemotron-super",
       "messages": [{"role": "user", "content": "Explain pipeline parallelism."}],
       "max_tokens": 2000}' | jq
```

## Step 8 — Benchmark with AIPerf

[manifests/aiperf-pod.yaml](manifests/aiperf-pod.yaml) — same in-cluster pattern as the nano guide, retargeted at the super service. `--concurrency=4 --request-count=80` matches the deployment's `--max-num-seqs=4` cap; raise both in lockstep.

> **Tip:** if you want to watch GPU utilization while the benchmark runs, set up [Live GPU monitoring](#live-gpu-monitoring-during-the-benchmark) **before** applying the Pod.

```bash
kubectl apply -f manifests/aiperf-pod.yaml
kubectl logs -f aiperf
```

The container stays up after `aiperf` exits so artifacts remain reachable. Press **Ctrl+C** on the log follow once you see the summary table, then:

```bash
kubectl cp aiperf:/workspace/artifacts ./aiperf-artifacts
kubectl delete pod aiperf
```

### Live GPU monitoring during the benchmark

[`nvitop`](https://github.com/XuehaiPan/nvitop) inside either pod (the pods have GPU access; your laptop doesn't):

```bash
kubectl exec -it vllm-nemotron-super-0   -- bash -c "pip install --quiet nvitop && nvitop"  # leader
kubectl exec -it vllm-nemotron-super-0-1 -- bash -c "pip install --quiet nvitop && nvitop"  # worker
```

`q` to exit.

## Cleanup

```bash
kubectl delete pod aiperf 2>/dev/null
kubectl delete -f manifests/service.yaml
envsubst '$AWS_REGION' < manifests/lws.yaml | kubectl delete -f -
envsubst < manifests/s3-storage.yaml | kubectl delete -f -

helm uninstall lws -n lws-system
kubectl delete namespace lws-system

eksctl delete cluster --name $CLUSTER_NAME --region $AWS_REGION

aws iam delete-policy --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/MountpointS3-${CLUSTER_NAME}
aws s3 rm s3://$S3_BUCKET --recursive && aws s3 rb s3://$S3_BUCKET
```

## Troubleshooting

- **Pod `Pending` / `Insufficient vpc.amazonaws.com/efa`** — EFA device plugin not running. Apply the manifest from Step 2.
- **NCCL hangs at `torch.distributed initialization`** — worker hasn't joined Ray. `kubectl exec vllm-nemotron-super-0 -- ray status` should show 16 GPUs across 2 nodes. If only 8, check worker logs for `LWS_LEADER_ADDRESS` resolution failures.
- **NCCL falls back to TCP / `EFA provider not found`** — confirm pod is privileged with `IPC_LOCK` and `FI_PROVIDER=efa` is set.
- **OOM during graph capture or KV-cache allocation** — BF16 leaves ~7 GB headroom per A10G. Drop `--max-num-seqs` to 2, `--gpu-memory-utilization` to 0.90, or `--max-model-len` to 4096.
- **`The quantization method modelopt is not supported for the current GPU. Minimum capability: 89.`** — `--model` is pointing at the FP8 checkpoint. Switch to the BF16 prefix; FP8 won't run on g5.
- **`Architecture NemotronHForCausalLM is not supported`** — DLC is too old. Use `vllm:0.20.0-gpu-py312-cu130-ubuntu22.04-ec2` or newer ([DLC tags](https://aws.github.io/deep-learning-containers/reference/available_images/#vllm)).
