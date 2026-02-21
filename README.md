# 📦 Semantic Backup Explorer

[![CI](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/dgaida/semantic-backup-explorer/branch/main/graph/badge.svg)](https://codecov.io/gh/dgaida/semantic-backup-explorer)

Ein Python-basiertes Tool zur **Synchronisation, Analyse und semantischen Durchsuchung von Backups** auf externen Festplatten.

Der Fokus liegt auf einer **einfachen Bedienung (One-Click Sync)**, auch ohne spezielle Hardware (GPU). Die semantische Suche über eine RAG-Pipeline ist ein optionales Feature.

---

## 🚀 Schnellstart (5 Minuten)

### 1. Installation

**Basis-Installation (nur Sync & Index):**
```bash
git clone https://github.com/dgaida/semantic-backup-explorer.git
cd semantic-backup-explorer
pip install -e .
```

**Vollständige Installation (inkl. Semantischer Suche):**
```bash
pip install -e ".[semantic]"
cp .env.example .env
# Trage deinen GROQ_API_KEY in .env ein
```

### 2. Web-App starten
```bash
python -m semantic_backup_explorer.cli.ui.gradio_app
```
Öffne http://localhost:7860 und starte deinen ersten Sync!

---

## ⚙️ Kernfunktionen

*   🔄 **One-Click Sync**: Vergleiche lokale Ordner blitzschnell mit deinem Backup und sichere fehlende Dateien mit nur einem Klick. Nutzt **Volume Labels** zur Sicherheit bei mehreren Laufwerken.
*   📄 **Backup-Index**: Erfasse die Struktur deiner Backup-Laufwerke als kompakte Markdown-Datei (`backup_index.md`).
*   🔍 **Semantische Suche (Optional)**: Nutze KI (LLMs), um deine Backups in natürlicher Sprache zu durchsuchen – auch wenn die Festplatte nicht angeschlossen ist.

---

## 🏗 Architektur

```
┌─────────────────┐
│  Gradio Web UI  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Sync & Compare  │◄─────┤ Backup Index │
│ (Core Logic)    │      │ (Markdown)   │
└────────┬────────┘      └──────────────┘
         │ (Optional)
         ▼
┌─────────────────┐      ┌──────────────┐
│ RAG Pipeline    │◄─────┤  ChromaDB    │
│ (Semantic)      │      │  (Embeddings)│
└─────────────────┘      └──────────────┘
```

---

## 📁 Projektstruktur

```
semantic_backup_explorer/
├── cli/            # CLI-spezifische Logik & UI
│   └── ui/         # Gradio Web Interface
├── core/           # Kern-Businesslogik (BackupOperations)
├── indexer/        # Scanning-Logik
├── chunking/       # Markdown Partitionierung (für RAG)
├── rag/            # Embedding & Retrieval (Optional)
├── compare/        # Folder Diffing
├── sync/           # Datei Synchronisation
├── utils/          # Hilfsfunktionen (Config, Logging, Paths)
└── exceptions.py   # Custom Exceptions
```

---

## ❓ Troubleshooting

### "GROQ_API_KEY nicht gefunden"
Stelle sicher, dass die `.env` Datei im Root-Verzeichnis existiert und einen gültigen API-Key enthält:
```bash
echo "GROQ_API_KEY=gsk_xxx" > .env
```

### "Python 3.14+ nicht unterstützt"
Das Projekt nutzt ChromaDB, welches aktuell Inkompatibilitäten mit Python 3.14+ aufweist. Nutze Python 3.10-3.13.

---

## 🛠 Entwicklung

Details zur Entwicklung, Testing und CI/CD findest du in der [CONTRIBUTING.md](CONTRIBUTING.md). Detailed documentation is available in the `docs/` folder.

### Tests ausführen
```bash
pytest
```

---

## 📜 Lizenz
MIT License
