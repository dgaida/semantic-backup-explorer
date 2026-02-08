\# 📦 Semantic Backup Explorer



Ein Python-basiertes Tool zur \*\*Analyse, semantischen Durchsuchung und Synchronisation von Backups\*\* auf externen Festplatten – mit einer \*\*Gradio Web-App\*\*, \*\*RAG-Pipeline\*\* und Anbindung an ein LLM über

👉 \[https://dgaida.github.io/llm\_client/](https://dgaida.github.io/llm\_client/)



---



\## 🚀 Motivation



Backups wachsen schnell – und werden unübersichtlich.



Dieses Projekt ermöglicht:



✅ Rekursives Erfassen kompletter Backup-Festplatten

✅ Speicherung der vollständigen Ordnerstruktur als Markdown

✅ Semantische Suche in Backups (RAG + LLM)

✅ Vergleich lokaler Ordner mit Backup-Ständen

✅ Visuelle Darstellung von Abweichungen

✅ One-Click-Synchronisation fehlender Dateien



---



\## 🧠 Kernfunktionen



\### 1. Backup-Struktur erfassen → Markdown



Ein Python-Skript:



\* durchläuft rekursiv externe Laufwerke

\* speichert \*\*jede Datei \& jeden Ordner mit vollem Pfad\*\*

\* schreibt alles in eine strukturierte `backup\_index.md`



Beispiel:



```md

\## /media/backup/photos/2022



\- /media/backup/photos/2022/img001.jpg

\- /media/backup/photos/2022/img002.jpg

```



---



\### 2. Semantische Suche mit RAG



\* Markdown wird in \*\*ordnerbasierte Chunks\*\* zerlegt

\* jeder Chunk = genau ein Ordner + enthaltene Dateien

\* Embeddings + Retrieval

\* Antwortgenerierung über LLM (`llm\_client`)



Du kannst z.B. fragen:



> "Wo liegen alte Steuerunterlagen von 2021?"

> "Welche Backups enthalten Projekt XY?"



---



\### 3. Ordnervergleich (lokal vs Backup)



In der Gradio App:



🔍 Lokaler Ordner wird ausgewählt

🔍 Entsprechender Backup-Ordner wird keyword-basiert gefunden

📊 Vergleich zeigt:



\* nur im Backup vorhanden

\* nur lokal vorhanden

\* in beiden vorhanden



---



\### 4. Backup-Synchronisation



Per Button:



➡️ alle fehlenden Dateien werden auf die externe Festplatte kopiert

(sobald angeschlossen)



---



\## 🖥 Gradio Web Interface



Mehrere Tabs:



| Tab                | Funktion             |

| ------------------ | -------------------- |

| 📚 Semantic Search | Fragen an das Backup |

| 📂 Folder Compare  | Lokal vs Backup      |

| 🔄 Sync            | Dateien kopieren     |

| 📄 Index Viewer    | Markdown anzeigen    |



---



\## 📁 Empfohlene Projektstruktur



```

semantic-backup-explorer/

│

├── README.md

├── requirements.txt

├── .env

│

├── data/

│   ├── backup\_index.md

│   ├── chunks/

│   └── embeddings/

│

├── src/

│   ├── indexer/

│   │   └── scan\_backup.py

│   │

│   ├── chunking/

│   │   └── folder\_chunker.py

│   │

│   ├── rag/

│   │   ├── embedder.py

│   │   ├── retriever.py

│   │   └── rag\_pipeline.py

│   │

│   ├── compare/

│   │   └── folder\_diff.py

│   │

│   ├── sync/

│   │   └── sync\_missing.py

│   │

│   └── app/

│       └── gradio\_app.py

│

└── scripts/

&nbsp;   └── build\_index.py

```



---



\## ⚙️ Installation



```bash

git clone https://github.com/yourname/semantic-backup-explorer.git

cd semantic-backup-explorer

pip install -r requirements.txt

```



---



\## 📦 Abhängigkeiten (Beispiel)



```

gradio

langchain

chromadb

sentence-transformers

llm-client

python-dotenv

tqdm

```



---



\## 📄 Backup Index erzeugen



```bash

python scripts/build\_index.py --path /media/external\_backup

```



Erzeugt:



```

data/backup\_index.md

```



---



\## 🌐 Gradio App starten



```bash

python src/app/gradio\_app.py

```



Dann im Browser:



```

http://localhost:7860

```



---



\## 🧩 RAG Architektur



```

Markdown → Ordner-Chunks → Embeddings → Vector DB

&nbsp;                                ↓

&nbsp;                             Retrieval

&nbsp;                                ↓

&nbsp;                             LLM Client

```



✔ Jeder Chunk entspricht genau einem Ordner

✔ Keine Fragmentierung einzelner Verzeichnisse



---



\## 🔐 LLM Integration



Dieses Projekt nutzt:



\[https://dgaida.github.io/llm\_client/](https://dgaida.github.io/llm\_client/)



Zur flexiblen Nutzung lokaler oder API-basierter Modelle.



---



\## 📊 Visualisierung



\* Dateilisten farblich markiert

\* nur Backup → 🔵

\* nur lokal → 🔴

\* beides → 🟢



Optional mit:



\* Tabellen

\* Tree Views

\* Diff-Listen



---



\## 🛣 Roadmap (optional)



\* \[ ] Hash-basierter Dateivergleich

\* \[ ] Versionierte Backups

\* \[ ] Zeitbasierte Snapshots

\* \[ ] Auto-Sync Scheduler

\* \[ ] Backup Health Report



---



\## 🧑‍💻 Zielgruppe



\* Entwickler:innen

\* Forschende

\* Power-User mit großen Backup-Archiven

\* Digitale Archivierung



---



\## 📜 Lizenz



MIT License

