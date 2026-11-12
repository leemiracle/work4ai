# LeRobot Annotate

A lightweight web UI for annotating LeRobot datasets with subtask segments and high-level dialogue. It works with any LeRobot dataset (local or Hugging Face Hub) and exports updated parquet files ready for training.

## What it produces

- `meta/subtasks.parquet` with unique subtasks.
- `meta/tasks_high_level.parquet` with high-level prompts/responses.
- Updated `data/chunk-*/file-*.parquet` files with:
  - `subtask_index`
  - `task_index_high_level`
- Annotation state saved to `meta/lerobot_annotations.json` for easy resume.

## Local usage

```bash
cd /admin/home/jade_choghari/lerobot-annotate
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --port 7860
```

Open `http://localhost:7860` in your browser.

### Workflow

1. **Connect dataset**
   - For HF datasets: enter repo ID (e.g. `lerobot/your-dataset`).
   - For local datasets: enter the dataset root path.
2. **Select an episode** from the left list to open its video.
3. **Add subtask segments** with start/end timestamps and labels.
4. **Add high-level segments** with user prompt + robot response (optional skill/scenario/response tags).
5. **Save episode** to persist annotations.
6. **Export** to write parquet updates and dataset metadata.

## Hugging Face Spaces (Docker)

1. Create a new Space and select **Docker**.
2. Point it to this repository.
3. The Space will build the provided `Dockerfile` and run `uvicorn` on port `7860`.

Optional environment variables:

- `LEROBOT_ANNOTATE_CACHE`: where HF datasets are downloaded (default `/tmp/lerobot_annotate_cache`).
- `LEROBOT_ANNOTATE_EXPORT`: where exports are written (default `/tmp/lerobot_annotate_exports`).

## Notes

- The tool only downloads `meta/` for Hub datasets on load. Video files are fetched on demand when you open an episode.
- Exports copy `meta/` and `data/` into a new output directory. Videos are symlinked by default (toggle “Copy videos” to duplicate them).
