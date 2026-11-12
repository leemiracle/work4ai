# Running Tests

To run the tests in this directory, you will first need to set the required environment variables. These variables provide the necessary credentials for the GitHub API and LLM service access.

## Required Environment Variables

The following environment variables must be set:

- `REPO_OWNER`: The owner of the repository where the test issues are located (e.g., `NVIDIA`).
- `REPO_NAME`: The name of the repository (e.g., `TensorRT`).
- `ACTION_TOKEN`: A GitHub token (e.g., a PAT) with permissions to read repository issues and labels.
- `LLM_TOKEN_CLIENT_ID`: Your client ID for the LLM service.
- `LLM_TOKEN_CLIENT_SECRET`: Your client secret for the LLM service.
- `LLM_TOKEN_SERVER_URL`: The token server URL for the LLM service.
- `LLM_GENERATE_URL`: The content generation endpoint URL for the LLM service.
- `LLM_TOKEN_SCOPE`: The scope required for the LLM access token.
- `LLM_MODEL_NAME`: The name of the LLM model to use (e.g., `gpt-4o`).

## Setting Environment Variables

You can set these variables in your shell before running `pytest`.

### Example

```bash
export REPO_OWNER="your_repo_owner"
export REPO_NAME="your_repo_name"
export ACTION_TOKEN="ghp_your_github_token"
export LLM_TOKEN_CLIENT_ID="your_client_id"
export LLM_TOKEN_CLIENT_SECRET="your_client_secret"
export LLM_TOKEN_SERVER_URL="https://your.token.server"
export LLM_GENERATE_URL="https://your.generate.endpoint"
export LLM_TOKEN_SCOPE="your_scope"
export LLM_MODEL_NAME="gpt-4o"

pytest
``` 