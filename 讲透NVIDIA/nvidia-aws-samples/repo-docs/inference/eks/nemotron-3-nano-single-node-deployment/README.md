# Nemotron 3 Nano on Amazon EKS with vLLM

End-to-end guide for deploying [nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) on Amazon EKS using the AWS Deep Learning Container (DLC) for vLLM.

## Architecture

```
┌───────────────────────────────────────────────────┐
│  EKS cluster (1.31)                               │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │  Managed node group: 1× g5.12xlarge         │  │
│  │  (4× A10G, 48 vCPU, 192 GiB, AL2-GPU AMI)   │  │
│  │                                             │  │
│  │   ┌───────────────────────────────────────┐ │  │
│  │   │ Pod: vllm-nemotron                    │ │  │
│  │   │  image: AWS vLLM DLC 0.20.0           │ │  │
│  │   │  --tensor-parallel-size 4             │ │  │
│  │   │  port 8000 (OpenAI-compatible API)    │ │  │
│  │   └───────────────────────────────────────┘ │  │
│  │           │ ReadOnlyMany mount              │  │
│  └───────────┼─────────────────────────────────┘  │
│              ▼                                    │
│       Mountpoint S3 CSI                           │
└──────────────┼────────────────────────────────────┘
               │
       ┌───────▼──────────────────┐
       │ S3 bucket                │
       │ nemotron-3-nano-bf16/    │
       │  ├── *.safetensors       │
       │  ├── tokenizer.json      │
       │  ├── nano_v3_reasoning…  │
       │  └── …                   │
       └──────────────────────────┘

  laptop ─── kubectl port-forward 8000:8000 ───▶ Service (ClusterIP)
```

Model weights and the `nano_v3` reasoning parser live in S3, mounted read-only via the [Mountpoint for Amazon S3 CSI driver](https://docs.aws.amazon.com/eks/latest/userguide/s3-csi.html) so replicas can fan out without re-downloading.

## Choosing the right vLLM DLC tag

Nemotron 3 Nano requires vLLM ≥ 0.12 (`NemotronHForCausalLM` architecture, `qwen3_coder` tool parser); older DLC tags like `vllm:0.9-gpu-py312-ec2` won't load it. This guide uses `vllm:0.20.0-gpu-py312-cu130-ubuntu22.04-ec2` from the AWS DLC ECR account `763104351884` (cross-region). Bump the tag as new vLLM versions ship — see [DLC tags](https://aws.github.io/deep-learning-containers/reference/available_images/#vllm).

## Prerequisites

- AWS CLI v2 configured (`aws sts get-caller-identity` should work)
- [eksctl](https://eksctl.io) ≥ 0.190
- `kubectl` ≥ 1.31
- A Hugging Face account with access to [nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) and a token (set `HF_TOKEN` locally) — used **once** during S3 staging, not at runtime
- The Hugging Face CLI: `pip install -U huggingface_hub` provides the `hf` command (Hugging Face renamed the legacy `huggingface-cli` to `hf` in `huggingface_hub` v1.0)
- ~70 GB of free local disk for staging the BF16 checkpoint, or a Linux EC2 box you can run the staging step from
- Service-quota headroom for `g5.12xlarge` in your target region (request via the [Service Quotas console](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas) → "Running On-Demand G and VT instances" — `g5.12xlarge` requires 48 vCPU)

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CLUSTER_NAME=nemotron-nano
export S3_BUCKET=nemotron-nano-models-${AWS_ACCOUNT_ID}-${AWS_REGION}
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

## Step 2 — Create the EKS cluster

[manifests/cluster.yaml](manifests/cluster.yaml) provisions a 1.31 control plane, a 1-node `g5.12xlarge` managed nodegroup (500 GiB gp3 root), and the `eks-pod-identity-agent` + `aws-mountpoint-s3-csi-driver` addons (CSI driver wired to the policy from Step 1). eksctl picks the EKS GPU AMI and auto-deploys the NVIDIA device plugin DaemonSet.

```bash
envsubst < manifests/cluster.yaml | eksctl create cluster -f -
```

~15–20 min. Verify:

```bash
kubectl describe node -l node.kubernetes.io/instance-type=g5.12xlarge | grep nvidia.com/gpu
# Capacity:  nvidia.com/gpu: 4
```

## Step 3 — Stage the model files to S3

Downloads the safetensors weights + `nano_v3_reasoning_parser.py` to the same S3 prefix the deployment will read from.

```bash
hf download nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --local-dir ./nemotron-3-nano-bf16

aws s3 sync ./nemotron-3-nano-bf16/ s3://$S3_BUCKET/nemotron-3-nano-bf16/
```

## Step 4 — Bind the bucket as a `ReadOnlyMany` PV

[manifests/s3-storage.yaml](manifests/s3-storage.yaml) wires `s3.csi.aws.com` to `$S3_BUCKET` as a `ReadOnlyMany` PV/PVC.

```bash
envsubst < manifests/s3-storage.yaml | kubectl apply -f -
```

## Step 5 — Deploy vLLM

[manifests/deployment.yaml](manifests/deployment.yaml) deploys vLLM 0.20.0 (DLC) with `--tensor-parallel-size=4 --max-model-len=16384`, the `qwen3_coder` tool parser, the `nano_v3` reasoning parser plugin, and `--served-model-name=nemotron`. Reads weights directly from the S3 mount.

```bash
envsubst < manifests/deployment.yaml | kubectl apply -f -
kubectl apply -f manifests/service.yaml
```

First boot streams weights from S3 and compiles CUDA graphs (~5–10 min):

```bash
kubectl logs -f -l app=vllm-nemotron
```

Ready when you see:

```
INFO ...  Application startup complete.
INFO ...  Uvicorn running on http://0.0.0.0:8000
```

## Step 6 — Connect from your laptop via port-forward

```bash
kubectl port-forward svc/vllm-nemotron 8000:8000
```

In another terminal — OpenAI-compatible API on `http://localhost:8000/v1`, model name `nemotron`:

```bash
# Reasoning ON (default)
curl -s http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "nemotron",
       "messages": [{"role": "user", "content": "Write a haiku about GPUs."}],
       "max_tokens": 4000}' | jq

# Reasoning OFF — pass chat_template_kwargs.enable_thinking=false
curl -s http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "nemotron",
       "messages": [{"role": "user", "content": "Give me 3 facts about vLLM."}],
       "max_tokens": 256,
       "chat_template_kwargs": {"enable_thinking": false}}' | jq
```

## Step 7 — Benchmark with AIPerf

[AIPerf](https://github.com/ai-dynamo/aiperf) (NVIDIA's LLM benchmarking tool, successor to `genai-perf`) ships preinstalled in the [Dynamo runtime container](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/ai-dynamo/containers/vllm-runtime). [manifests/aiperf-pod.yaml](manifests/aiperf-pod.yaml) runs it in-cluster against `http://vllm-nemotron:8000` with `--concurrency=8 --request-count=200 --isl=1024 --osl=2000 --streaming`, using the tokenizer from the S3 PVC. AIPerf auto-detects `reasoning_content` and reports separate **Reasoning Metrics** + **TTFO** vs **TTFT**.

> **Tip:** set up [Live GPU monitoring](#live-gpu-monitoring-during-the-benchmark) in a separate terminal **before** applying the Pod — the run only takes a couple of minutes.

```bash
kubectl apply -f manifests/aiperf-pod.yaml
kubectl logs -f aiperf
```

The container stays up after `aiperf` exits so artifacts remain reachable. Press **Ctrl+C** on the log follow once you see the summary, then:

```bash
kubectl cp aiperf:/workspace/artifacts ./aiperf-artifacts
kubectl delete pod aiperf
```

To re-run with different settings, edit `args:` in [manifests/aiperf-pod.yaml](manifests/aiperf-pod.yaml), `kubectl delete pod aiperf`, re-apply.

### Live GPU monitoring during the benchmark

[`nvitop`](https://github.com/XuehaiPan/nvitop) inside the pod (the pod has GPU access; your laptop doesn't):

```bash
kubectl exec -it deploy/vllm-nemotron -- bash -c "pip install --quiet nvitop && nvitop"
```

`q` to exit.

## Cleanup

```bash
kubectl delete -f manifests/service.yaml
envsubst < manifests/deployment.yaml | kubectl delete -f -
envsubst < manifests/s3-storage.yaml | kubectl delete -f -

eksctl delete cluster --name $CLUSTER_NAME --region $AWS_REGION

aws iam delete-policy --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/MountpointS3-${CLUSTER_NAME}
aws s3 rm s3://$S3_BUCKET --recursive && aws s3 rb s3://$S3_BUCKET
```

## Troubleshooting

- **Pod `Pending` / `Insufficient nvidia.com/gpu`** — device plugin not yet registered. Wait for `kubectl get pods -n kube-system | grep nvidia` to be Running.
- **OOM during model load** — lower `--max-model-len` or raise `--gpu-memory-utilization` cautiously.
- **`Architecture NemotronHForCausalLM is not supported`** — DLC tag is too old. Use `vllm:0.20.0-gpu-py312-cu130-ubuntu22.04-ec2` or newer.
- **`MountVolume.SetUp failed ... AccessDenied`** — the Mountpoint S3 CSI service account isn't bound to the IAM policy. Verify `kubectl get sa s3-csi-driver-sa -n kube-system -o yaml` shows an `eks.amazonaws.com/role-arn` annotation linked to the policy from Step 1.
- **Mount succeeds but pod logs `FileNotFoundError: /models/nemotron-3-nano-bf16/config.json`** — S3 prefix mismatch. `aws s3 ls s3://$S3_BUCKET/nemotron-3-nano-bf16/` should list the model files.
