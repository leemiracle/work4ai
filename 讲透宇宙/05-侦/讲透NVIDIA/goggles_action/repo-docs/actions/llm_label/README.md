# LLM Auto-Labeling Action

This GitHub Action automatically labels issues using a Language Model (LLM) and a repository's predefined labels.

## How It Works

The action processes new issues by:
1.  Fetching the issue's title and body.
2.  Retrieving the list of available labels (including their descriptions) from the repository.
3.  Obtaining an access token from the configured token server.
4.  Use the access token retrieved from previuos step to send issue details and available labels to an LLM to get label suggestions.
5.  Validating the LLM's suggestions against the repository's actual labels.
6.  Appending the valid, new suggested labels to the issue.

## Setup and Usage

### 1. Configure LLM Service Access

Ensure the following are configured as secrets or variables in your repository (under `Settings > Secrets and variables > Actions`):

*   `LLM_TOKEN_SERVER_URL`: URL for the LLM authentication token server.
*   `LLM_TOKEN_CLIENT_ID`: Client ID for LLM token authentication.
*   `LLM_TOKEN_CLIENT_SECRET`: Client Secret for LLM token authentication.
*   `LLM_GENERATE_URL`: URL for the LLM content generation endpoint.
*   `LLM_TOKEN_SCOPE`: The specific scope required by your LLM token server for token acquisition.
*   `LLM_MODEL_NAME`: (Optional) LLM model name (e.g., `gpt-4o`). Defaults to the model in `action.yml`.

### 2. Add to Workflow

In your GitHub Actions workflow (e.g., `.github/workflows/main.yml`), add a step to use this action.

**Core Configuration:**

```yaml
- name: LLM Label Issue
  uses: poweiw/goggles_action/action_llm_label@main # Replace with your actual path if forked/different
  with:
    ACTION_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    LLM_TOKEN_SERVER_URL: ${{ secrets.LLM_TOKEN_SERVER_URL }}
    LLM_TOKEN_CLIENT_ID: ${{ secrets.LLM_TOKEN_CLIENT_ID }}
    LLM_TOKEN_CLIENT_SECRET: ${{ secrets.LLM_TOKEN_CLIENT_SECRET }}
    LLM_GENERATE_URL: ${{ secrets.LLM_GENERATE_URL }}
    LLM_TOKEN_SCOPE: ${{ secrets.LLM_TOKEN_SCOPE }}
    # LLM_MODEL_NAME: "gpt-4o" # Optional: to override default model
```

### Permissions

Ensure your workflow has the following permissions:

```yaml
permissions:
  issues: write   # to add labels to issues
  contents: read  # to checkout the action repository
```

## Triage Demo Script (`triage_demo.py`)

The `triage_demo.py` script provides a command-line interface to test and demonstrate the LLM-based triaging functionality locally before deploying it to GitHub.

### Usage

The script requires several arguments to interact with the GitHub API and the LLM service.

**Prerequisites:**
*   Python 3.x installed.
*   Required Python packages (inspect `triage_demo.py` for imports, typically `requests`). You might need to install them using pip:
    ```bash
    pip install requests 
    ```

**Running the script:**

```bash
python triage_demo.py --repo_url "OWNER/REPO" \
                      --item_number YOUR_ISSUE_OR_PR_NUMBER \
                      --github_token YOUR_GITHUB_TOKEN \
                      --llm_token_client_id YOUR_LLM_CLIENT_ID \
                      --llm_token_client_secret YOUR_LLM_CLIENT_SECRET \
                      --llm_token_server_url YOUR_LLM_TOKEN_SERVER_URL \
                      --llm_generate_url YOUR_LLM_GENERATE_URL \
                      --llm_model_name "YOUR_LLM_MODEL_NAME" \
                      --llm_token_scope YOUR_LLM_TOKEN_SCOPE \
                      [--verbose]
```
See detailed descriptions of each command line argument with `python triage_demo.py -h`

This script will fetch the specified issue/PR, get label suggestions from the LLM, and print the valid new suggestions. It does not modify the issue/PR on GitHub. 