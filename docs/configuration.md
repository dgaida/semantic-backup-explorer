# Configuration

The Semantic Backup Explorer uses environment variables and a centralized configuration class for management.

## Central Configuration (`BackupConfig`)

The `BackupConfig` class in `semantic_backup_explorer/utils/config.py` defines the default settings:

- `backup_drive`: The root path of your backup drive (default: `/media/backup`).
- **Drive Labels (Windows)**: The indexer automatically detects the volume label of your drive on Windows. This information is included in the index to provide better context for the KI search.
- `index_path`: Path to the generated Markdown index file (default: `data/backup_index.md`).
- `embeddings_path`: Directory for ChromaDB storage (default: `data/embeddings`).
- `groq_api_key`: Your Groq API key for the RAG pipeline.

## Environment Variables

You can override these defaults by creating a `.env` file in the project root:

```env
BACKUP_DRIVE=/path/to/my/external/drive
INDEX_PATH=data/my_backup.md
EMBEDDINGS_PATH=data/my_embeddings
GROQ_API_KEY=gsk_your_key_here
```

## Backup Configuration (`backup_config.md`)

For the `auto_sync.py` script, you define which local folders should be tracked in a Markdown file:

```markdown
## Source Folders
- /home/user/Documents
- /home/user/Pictures/2023
```

The script will attempt to find a matching folder on the backup drive for each entry listed here.
