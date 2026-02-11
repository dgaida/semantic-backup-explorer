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

- **Semantic Search**: Nutze natürliche Sprache. Frage z.B. "Wo liegen meine alten Steuererklärungen?". Die KI durchsucht den Index und nennt dir die wahrscheinlichsten Ordner.
- **Folder Compare**:
    1. Klicke auf "Ordner wählen" und suche den lokalen Ordner aus, den du abgleichen möchtest.
    2. Klicke auf "Vergleichen".
    3. Die App sucht automatisch das passende Gegenstück auf deinem Backup-Laufwerk (basierend auf dem Namen oder via KI).
    4. In der Liste "Nur Lokal" siehst du alle Dateien, die noch nicht im Backup sind.
- **Synchronisieren**: Wenn du im Tab "Folder Compare" bist und Unterschiede gefunden wurden, klicke auf "Synchronisieren", um die fehlenden Dateien direkt auf die externe Festplatte zu kopieren.

## Schritt-für-Schritt für Einsteiger

### 1. Vorbereitung
Schließe dein Backup-Laufwerk (z.B. eine USB-Festplatte) an deinen Computer an.

### 2. Den Index erstellen
Gehe zum Tab **Index Viewer**. Wähle über den Button "Ordner wählen" dein Backup-Laufwerk aus (z.B. `E:\`). Klicke auf **Index erstellen**. Die App scannt nun alle Dateien. Das kann je nach Größe der Festplatte ein paar Minuten dauern.

### 3. KI-Suche aktivieren
Gehe zum Tab **Semantic Search**. Klicke auf den Button **Embeddings erstellen**. Dieser Schritt ist wichtig, damit die KI die Ordnerstruktur "verstehen" kann. Dies muss nur einmal nach dem Erstellen eines neuen Index gemacht werden.

### 4. Suchen und Abgleichen
Jetzt kannst du über die Suche Ordner finden oder über den Tab **Folder Compare** deine tägliche Arbeit sichern.

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
