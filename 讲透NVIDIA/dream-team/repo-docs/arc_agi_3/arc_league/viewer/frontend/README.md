# TeamSolver run viewer frontend

This React and TypeScript application is the browser interface for the local
TeamSolver run viewer.

Build the static application with:

```bash
npm ci
npm run build
```

Vite writes the output to `../static`, where the FastAPI server serves it. From
the repository root, start that server with:

```bash
python -m arc_agi_3.arc_league.viewer \
  --results-dir results/arc_agi_3 \
  --host 127.0.0.1 \
  --port 8420
```

The viewer has no authentication. Keep it bound to localhost and use only
trusted run directories.
