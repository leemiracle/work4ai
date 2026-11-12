# pi-local-router

Pi extension that routes between a local llama.cpp model and a remote Hugging Face Inference Providers model.

The router first asks the local model to classify whether the current request is safe for local handling. If that route probe passes, it asks the local model for a short answer with logprobs enabled. Pi returns the local answer only when both the route probe and token entropy/top-1 confidence pass. Otherwise Pi sends the same conversation to the remote Hugging Face model.

## Setup

Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

Start a local llama.cpp OpenAI-compatible server on port `8081`:

```bash
llama-server --port 8081 --jinja --logits-all --model /path/to/model.gguf
```

Find the model id exposed by llama.cpp:

```bash
MODEL_ID="$(curl -s http://127.0.0.1:8081/v1/models | jq -r '.data[0].id')"
echo "$MODEL_ID"
```

Start the local router server:

```bash
export LOCAL_ROUTER_MODEL_ID="$MODEL_ID"
export LOCAL_ROUTER_BACKEND_BASE_URL=http://127.0.0.1:8081/v1
python -m local_router.server
```

In another shell, run Pi with the extension:

```bash
export HF_TOKEN=hf_...
export ROUTER_LOCAL_MODEL="$MODEL_ID"
export ROUTER_REMOTE_MODEL=zai-org/GLM-5.2:fastest
export ROUTER_LOCAL_BASE_URL=http://127.0.0.1:8080/v1

scripts/pi-router.sh
```

Or run the explicit Pi command:

```bash
pi -e /path/to/pi-local-router --model local-router/local-to-hf
```

The Pi footer should show `(local-router) local-to-hf`. If it shows a built-in provider such as `(huggingface) zai-org/GLM-5.2`, Pi is bypassing the router. Inside Pi, run `/router-use` to switch to the router model and `/router-status` to check the local router server.

## Useful Knobs

```bash
export ROUTER_ENTROPY_THRESHOLD=0.12
export ROUTER_TOP1_THRESHOLD=0.95
export ROUTER_CONFIDENCE_THRESHOLD=0.97
export ROUTER_SHOW_TRACE=1
export ROUTER_AUTO_SELECT=1
export LOCAL_ROUTER_ROUTE_PROBE=1
export LOCAL_ROUTER_ROUTE_PROBE_CONFIDENCE_THRESHOLD=0.80
export LOCAL_ROUTER_ROUTE_PROBE_MAX_TOKENS=64
export LOCAL_ROUTER_PROBE_MAX_CONTEXT_CHARS=12000
export LOCAL_ROUTER_PROBE_MAX_MESSAGE_CHARS=4000
```

Remote routes require `HF_TOKEN`, `HUGGINGFACE_API_KEY`, or `HUGGING_FACE_HUB_TOKEN`.

Run checks:

```bash
npm test
npm run eval:mock
```
