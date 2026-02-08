# 📦 Semantic Backup Explorer

Ein Python-basiertes Tool zur **Analyse, semantischen Durchsuchung und Synchronisation von Backups** auf externen Festplatten – mit einer **Gradio Web-App**, **RAG-Pipeline** und Anbindung an ein LLM über
👉 [https://dgaida.github.io/llm_client/](https://dgaida.github.io/llm_client/)

---

## 🚀 Motivation

Backups wachsen schnell – und werden unübersichtlich.

Dieses Projekt ermöglicht:

✅ Rekursives Erfassen kompletter Backup-Festplatten  
✅ Speicherung der vollständigen Ordnerstruktur als Markdown  
✅ Semantische Suche in Backups (RAG + LLM)  
✅ Vergleich lokaler Ordner mit Backup-Ständen  
✅ Visuelle Darstellung von Abweichungen  
✅ One-Click-Synchronisation fehlender Dateien

---

## 🧠 Kernfunktionen

### 1. Backup-Struktur erfassen → Markdown

Ein Python-Skript:

* durchläuft rekursiv externe Laufwerke
* speichert **jede Datei & jeden Ordner mit vollem Pfad**
* schreibt alles in eine strukturierte `backup_index.md`

Beispiel:

```md
## /media/backup/photos/2022

- /media/backup/photos/2022/img001.jpg
- /media/backup/photos/2022/img002.jpg
```

---

### 2. Semantische Suche mit RAG

* Markdown wird in **ordnerbasierte Chunks** zerlegt
* jeder Chunk = genau ein Ordner + enthaltene Dateien
* Embeddings + Retrieval
* Antwortgenerierung über LLM (`llm_client`)

Beispiel-Fragen:

> Wo liegen alte Steuerunterlagen von 2021?
> Welche Backups enthalten Projekt XY?

---

### 3. Ordnervergleich (lokal vs Backup)

In der Gradio App:

🔍 Lokaler Ordner auswählen  
🔍 Entsprechender Backup-Ordner wird keyword-basiert gefunden  
📊 Vergleich zeigt:

* nur im Backup vorhanden
* nur lokal vorhanden
* in beiden vorhanden

---

### 4. Backup-Synchronisation

Per Button:

➡️ alle fehlenden Dateien werden auf die externe Festplatte kopiert
(sobald angeschlossen)

---

## 🖥 Gradio Web Interface

Mehrere Tabs:

| Tab                | Funktion             |
| ------------------ | -------------------- |
| 📚 Semantic Search | Fragen an das Backup |
| 📂 Folder Compare  | Lokal vs Backup      |
| 🔄 Sync            | Dateien kopieren     |
| 📄 Index Viewer    | Markdown anzeigen    |

---

## 📁 Empfohlene Projektstruktur

```
semantic-backup-explorer/
│
├── README.md
├── requirements.txt
├── .env
│
├── data/
│   ├── backup_index.md
│   ├── chunks/
│   └── embeddings/
│
├── src/
│   ├── indexer/
│   │   └── scan_backup.py
│   │
│   ├── chunking/
│   │   └── folder_chunker.py
│   │
│   ├── rag/
│   │   ├── embedder.py
│   │   ├── retriever.py
│   │   └── rag_pipeline.py
│   │
│   ├── compare/
│   │   └── folder_diff.py
│   │
│   ├── sync/
│   │   └── sync_missing.py
│   │
│   └── app/
│       └── gradio_app.py
│
└── scripts/
    └── build_index.py
```

---

## ⚙️ Installation

**Requirements:** Python 3.10, 3.11, 3.12 or 3.13.
*(Note: Python 3.14+ is currently not supported due to dependency incompatibilities.)*

```bash
git clone https://github.com/yourname/semantic-backup-explorer.git
cd semantic-backup-explorer
pip install -r requirements.txt
```

---

## 📦 Abhängigkeiten (Beispiel)

```
gradian
langchain
chromadb
sentence-transformers
llm-client
python-dotenv
tqdm
```

---

## 📄 Backup Index erzeugen

```bash
python scripts/build_index.py --path /media/external_backup
```

Erzeugt:

```
data/backup_index.md
```

---

## 🌐 Gradio App starten

```bash
python semantic_backup_explorer/app/gradio_app.py
```

Browser:

```
http://localhost:7860
```

---

## 🧩 RAG Architektur

```
Markdown → Ordner-Chunks → Embeddings → Vector DB
                                 ↓
                              Retrieval
                                 ↓
                              LLM Client
```

✔ Jeder Chunk entspricht genau einem Ordner
✔ Keine Fragmentierung einzelner Verzeichnisse

---

## 📊 Visualisierung

* 🔵 nur im Backup
* 🔴 nur lokal
* 🟢 in beiden vorhanden

Optional mit Tabellen oder Tree Views.

---

## 🛣 Roadmap

* [ ] Hash-basierter Dateivergleich
* [ ] Versionierte Backups
* [ ] Zeitbasierte Snapshots
* [ ] Auto-Sync Scheduler
* [ ] Backup Health Report

---

## 📜 Lizenz

MIT License
