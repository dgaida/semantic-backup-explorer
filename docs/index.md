# 📦 Semantic Backup Explorer

[![CI](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/dgaida/semantic-backup-explorer/actions/workflows/ci.yml)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/dgaida/semantic-backup-explorer/branch/main/graph/badge.svg)](https://codecov.io/gh/dgaida/semantic-backup-explorer)

Ein Python-basiertes Tool zur **Analyse, semantischen Durchsuchung und Synchronisation von Backups** auf externen Festplatten.

Der Semantic Backup Explorer hilft dir dabei, den Überblick über deine verstreuten Backups auf verschiedenen externen Laufwerken zu behalten. Er nutzt modernste KI-Technologie (Large Language Models), um deine Dateien auffindbar zu machen – sogar wenn du den genauen Namen eines Ordners vergessen hast!

---

## 🤔 Warum Semantic Backup Explorer?

Hast du mehrere externe Festplatten und suchst verzweifelt nach den Hochzeitsfotos von vor 5 Jahren oder den Steuerunterlagen aus 2018? Normalerweise müsstest du jede Platte anschließen und manuell durchsuchen.

**Hier kommt der Semantic Backup Explorer ins Spiel:**

1.  **Einmal Scannen (Indizieren):** Die App liest einmalig die Struktur deiner Festplatte ein und speichert sie in einem kompakten "Index" (einer Textdatei).
2.  **Suchen ohne Hardware:** Du kannst deine Backups durchsuchen, **ohne** dass die Festplatten angeschlossen sein müssen. Die KI versteht Zusammenhänge (z.B. findet sie "Rechnungen", wenn du nach "Finanzen" suchst).
3.  **Intelligenter Abgleich:** Wenn du weißt, auf welcher Platte das Backup liegt, hilft dir die App dabei, deinen aktuellen Arbeitsordner mit dem Backup zu vergleichen und nur die neuen Dateien zu sichern.

---

## 🌟 Hauptfunktionen

*   🔍 **Semantische Suche**: Frage einfach: "Wo habe ich meine Python-Projekte gesichert?"
*   📂 **Ordner-Vergleich**: Sieh auf einen Blick, welche Dateien lokal vorhanden sind, aber im Backup fehlen.
*   🔄 **One-Click Sync**: Kopiere fehlende Dateien direkt auf das Backup-Laufwerk.
*   🏷️ **Laufwerks-Erkennung**: Erkennt automatisch den Namen (Label) deiner Festplatten unter Windows.

---

## 🚀 Schnellstart (5 Minuten)

### 1. Installation
```bash
git clone https://github.com/dgaida/semantic-backup-explorer.git
cd semantic-backup-explorer
pip install -e .
cp .env.example .env
# Trage deine API-Keys (GROQ_API_KEY) in .env ein
```

### 2. Ersten Index erstellen
```bash
python scripts/build_index.py --path /path/to/backup
```

### 3. Web-App starten
```bash
python -m semantic_backup_explorer.cli.ui.gradio_app
```
Öffne http://localhost:7860 und stelle deine erste Frage!

---

## 🏗 Architektur

```
┌─────────────────┐
│  Gradio Web UI  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ RAG Pipeline    │◄─────┤  ChromaDB    │
│ (Core Logic)    │      │  (Embeddings)│
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Backup Index    │◄─────┤  LLM Client  │
│ (Markdown)      │      │  (Groq)      │
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

* **Backup-Struktur erfassen**: Rekursives Scanning und Speicherung als Markdown (`backup_index.md`).
* **Semantische Suche (RAG)**: Ordnerbasierte Chunking-Logik ermöglicht präzise Suche in Backup-Strukturen via LLM.
* **Intelligenter Ordnervergleich**: Lokale Ordner werden automatisch (keyword-basiert oder via RAG) ihrem Backup-Gegenstück zugeordnet und verglichen.
* **One-Click Sync**: Fehlende oder neuere lokale Dateien werden direkt auf das Backup-Laufwerk synchronisiert.

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
