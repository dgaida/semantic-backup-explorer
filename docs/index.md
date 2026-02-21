# 📦 Semantic Backup Explorer

[![CI](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/dgaida/semantic-backup-explorer/branch/main/graph/badge.svg)](https://codecov.io/gh/dgaida/semantic-backup-explorer)

Ein Python-basiertes Tool zur **Synchronisation, Analyse und semantischen Durchsuchung von Backups** auf externen Festplatten.

Der Semantic Backup Explorer hilft dir dabei, den Überblick über deine verstreuten Backups auf verschiedenen externen Laufwerken zu behalten. Der Fokus liegt auf einem einfachen **One-Click Sync**, um deine tägliche Arbeit schnell und unkompliziert zu sichern. Optional kannst du modernste KI-Technologie (Large Language Models) nutzen, um deine Dateien auffindbar zu machen.

---

## 🤔 Warum Semantic Backup Explorer?

Hast du mehrere externe Festplatten und möchtest sicherstellen, dass dein aktuelles Projekt auf dem richtigen Backup-Stand ist? Oder suchst du verzweifelt nach Dateien, ohne jede Platte einzeln anschließen zu wollen?

**Hier kommt der Semantic Backup Explorer ins Spiel:**

1.  **Blitzschneller Abgleich (One-Click Sync):** Wähle einen lokalen Ordner, und die App findet automatisch das passende Backup-Gegenstück und zeigt dir, was fehlt.
2.  **Kompakter Index:** Die App speichert die Struktur deiner Festplatte in einer kleinen Textdatei. So weißt du immer, was wo liegt, auch wenn die Platte im Schrank liegt.
3.  **KI-Suche (Optional):** Die KI versteht Zusammenhänge (z.B. findet sie "Rechnungen", wenn du nach "Finanzen" suchst) und hilft dir, den richtigen Backup-Ordner zu finden.

---

## 🌟 Hauptfunktionen

*   🔄 **One-Click Sync**: Kopiere fehlende oder neuere Dateien mit nur einem Klick auf dein Backup-Laufwerk.
*   📂 **Intelligenter Abgleich**: Findet automatisch den richtigen Zielordner auf deinem Backup.
*   🔍 **Semantische Suche (Optional)**: Frage einfach: "Wo habe ich meine Python-Projekte gesichert?"
*   🏷️ **Laufwerks-Erkennung**: Erkennt automatisch den Namen (Label) deiner Festplatten unter Windows.

---

## 🚀 Schnellstart (5 Minuten)

### 1. Installation

**Basis (Sync & Index):**
```bash
git clone https://github.com/dgaida/semantic-backup-explorer.git
cd semantic-backup-explorer
pip install -e .
```

**Optional (Semantische Suche):**
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
│   ├── commands/   # Zukünftige CLI Commands
│   └── ui/         # Gradio Web Interface
├── core/           # Kern-Businesslogik (BackupOperations)
├── indexer/        # Scanning-Logik
├── chunking/       # Markdown Partitionierung
├── rag/            # Embedding & Retrieval
├── compare/        # Folder Diffing
├── sync/           # Datei Synchronisation
├── utils/          # Hilfsfunktionen (Config, Logging, Paths)
└── exceptions.py   # Custom Exceptions
```

---

## ⚙️ Kernfunktionen

*   🔄 **One-Click Sync**: Kopiere fehlende oder neuere Dateien mit nur einem Klick auf dein Backup-Laufwerk.
*   📄 **Backup-Index**: Erfasse die Struktur deiner Backup-Laufwerke als kompakte Markdown-Datei.
*   🔍 **Semantische Suche (Optional)**: Nutze KI (LLMs), um deine Backups in natürlicher Sprache zu durchsuchen.

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
