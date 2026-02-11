# Usage Guide

This guide provides examples for both the CLI scripts and the Web UI.

## Initial Setup

Before using the tool, you must create an index of your backup drive:

```bash
python scripts/build_index.py --path /media/external_backup
```

This command will:
1. Scan the drive and create `data/backup_index.md`.
2. Generate embeddings and store them in the vector database.

## Web Interface

Start the Gradio app:

```bash
python -m semantic_backup_explorer.cli.ui.gradio_app
```

Navigate to `http://localhost:7860` in your browser.

- **Semantic Search**: Ask questions like "Where are my tax documents?"
- **Folder Compare**: Enter a local path and click "Vergleichen". The app will find the backup folder and show you what is missing.
- **Synchronisieren**: Click the sync button to copy missing local files to the backup.

## Automated Sync

To sync all folders defined in your `backup_config.md`:

```bash
python scripts/auto_sync.py --backup_path /media/external_backup
```

This script will:
1. Re-scan the backup drive to ensure the index is up-to-date.
2. Iterate through each source folder.
3. Compare and copy missing files.
4. Print a summary protocol at the end.

## Troubleshooting

- **No matching folder found**: Ensure the local folder name is reasonably similar to the folder name in the backup.
- **RAG Errors**: Check your `GROQ_API_KEY` in the `.env` file.
- **Stale Embeddings**: If you manually edited files on the backup, rebuild the index via the UI or `build_index.py`.
