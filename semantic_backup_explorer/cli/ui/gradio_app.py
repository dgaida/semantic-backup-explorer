"""Gradio Web UI for Semantic Backup Explorer."""

import logging
import os
from pathlib import Path
from typing import Any, NamedTuple, Optional

import gradio as gr

from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown
from semantic_backup_explorer.core.backup_operations import BackupOperations
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.utils.index_utils import get_index_metadata
from semantic_backup_explorer.rag.embedder import Embedder
from semantic_backup_explorer.rag.rag_pipeline import RAGPipeline
from semantic_backup_explorer.rag.retriever import Retriever
from semantic_backup_explorer.sync.sync_missing import sync_files
from semantic_backup_explorer.utils.compatibility import check_python_version
from semantic_backup_explorer.utils.config import BackupConfig

check_python_version()

logger = logging.getLogger(__name__)

# Initialize Config
config = BackupConfig()

# Initialize RAG Pipeline
pipeline: Optional[RAGPipeline]
try:
    pipeline = RAGPipeline()
except Exception as e:
    logger.error(f"Could not initialize RAG Pipeline: {e}")
    pipeline = None

# Initialize Backup Operations
operations = BackupOperations(index_path=config.index_path, rag_pipeline=pipeline)


def select_folder() -> str:
    """Opens a native folder selection dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        # Bring dialog to front
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory()
        root.destroy()
        return folder
    except Exception as e:
        logger.error(f"Error opening folder dialog: {e}")
        return ""


def semantic_search(query: str) -> tuple[str, str]:
    """Handles semantic search queries."""
    if not pipeline:
        return "RAG Pipeline not initialized. Check GROQ_API_KEY.", ""
    answer, context = pipeline.answer_question(query)
    return answer, context


class ComparisonUIResult(NamedTuple):
    """Result of folder comparison for UI."""

    status: str
    only_local: str
    only_backup: str
    in_both: str
    target_root: str


def get_index_status_html() -> str:
    """Returns a formatted HTML string with index status info."""
    metadata = get_index_metadata(config.index_path)
    if not metadata.root_path:
        return (
            "<div style='color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;'>"
            "⚠️ Kein Backup-Index gefunden. Bitte erstelle einen Index im Tab 'Index Viewer'."
            "</div>"
        )

    date_str = metadata.mtime.strftime("%d.%m.%Y %H:%M") if metadata.mtime else "Unbekannt"
    label_str = f" (Label: {metadata.label})" if metadata.label else ""

    html = f"""
    <div style='background-color: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; border: 1px solid #bee5eb;'>
        <b>Gelesener Backup-Index (backup_index.md)</b><br>
        Laufwerk: <code>{metadata.root_path}</code>{label_str}<br>
        Erstellt am: {date_str} ({metadata.age_days} Tage alt)
    </div>
    """

    if metadata.age_days > 7:
        html += """
        <div style='color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #f5c6cb;'>
            ⚠️ <b>Hinweis:</b> Der Index ist älter als 7 Tage. Bitte aktualisiere ihn im Tab 'Index Viewer', um sicherzustellen, dass alle Änderungen auf dem Backup erfasst sind.
        </div>
        """
    return html


def folder_compare(local_path_str: str) -> ComparisonUIResult:
    """Compares local folder with backup for UI."""
    if not local_path_str:
        return ComparisonUIResult("Bitte Pfad eingeben.", "", "", "", "")

    local_path = Path(local_path_str)
    if not local_path.exists():
        return ComparisonUIResult("Lokaler Pfad existiert nicht.", "", "", "", "")

    result = operations.find_and_compare(local_path)

    if result.error:
        return ComparisonUIResult(f"⚠️ {result.error}", "\n".join(result.only_local), "", "", "")

    metadata = get_index_metadata(config.index_path)
    label_info = f" (Label: {metadata.label})" if metadata.label else ""

    return ComparisonUIResult(
        status=f"✅ Gefundenes Backup im Index{label_info}: {result.backup_path}",
        only_local="\n".join(result.only_local),
        only_backup="\n".join(result.only_backup),
        in_both="\n".join(result.in_both),
        target_root=str(result.backup_path),
    )


def run_sync(only_local_text: str, local_root_str: str, target_root_str: str, progress: gr.Progress = gr.Progress()) -> str:
    """Runs the file synchronization process."""
    # Safety check: Verify the drive again before syncing
    is_correct, error = operations.verify_backup_drive()
    if not is_correct:
        return f"Fehler: {error}"

    if not target_root_str or not os.path.exists(target_root_str):
        return "Zielordner existiert nicht oder ist nicht angeschlossen."

    files_to_sync = [f.strip() for f in only_local_text.split("\n") if f.strip()]
    if not files_to_sync:
        return "Keine Dateien zum Synchronisieren."

    def sync_callback(current: int, total: int, filename: str, error: Optional[str] = None) -> None:
        if error:
            desc = f"⚠️ Fehler bei {filename}: {error}"
        else:
            desc = f"Kopiere Datei {current} von {total}..."
            if current == 1 or current == total or current % 100 == 0:
                desc += f" ({filename})"
        progress(current / total, desc=desc)

    synced, errors = sync_files(files_to_sync, local_root_str, target_root_str, callback=sync_callback)

    msg = f"{len(synced)} Dateien erfolgreich kopiert."
    if errors:
        msg += f"\nFehler bei {len(errors)} Dateien."
    return msg


def get_index_viewer() -> str:
    """Reads the backup index file for viewing."""
    if config.index_path.exists():
        with open(config.index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Kein Index gefunden. Bitte oben den Pfad angeben und auf 'Index erstellen' klicken."


def create_index(backup_path: str, progress: gr.Progress = gr.Progress()) -> tuple[str, str]:
    """Creates a new backup index."""
    if not backup_path or not os.path.exists(backup_path):
        return "Ungültiger Pfad.", get_index_viewer()

    def scan_callback(count: int, current_folder: str) -> None:
        if count == 1 or count % 100 == 0:
            progress(None, desc=f"Gelesene Ordner: {count}... Aktuell: {current_folder}")

    try:
        scan_backup(backup_path, output_file=config.index_path, callback=scan_callback)
        return "Index erfolgreich erstellt.", get_index_viewer()
    except Exception as e:
        logger.exception("Error during indexing")
        return f"Fehler beim Erstellen des Index: {e}", get_index_viewer()


def check_embeddings_staleness() -> tuple[dict[str, Any], dict[str, Any]]:
    """Checks if embeddings need rebuilding."""
    embeddings_file = config.embeddings_path / "chroma.sqlite3"

    if not config.index_path.exists():
        return gr.update(visible=False), gr.update(visible=False)

    if not embeddings_file.exists():
        return gr.update(value="⚠️ Embeddings fehlen. Bitte erstellen.", visible=True), gr.update(visible=True)

    if embeddings_file.stat().st_mtime < config.index_path.stat().st_mtime:
        return gr.update(value="⚠️ Die Embeddings sind veraltet und müssen erneuert werden.", visible=True), gr.update(
            visible=True
        )

    return gr.update(visible=False), gr.update(visible=False)


def run_rebuild_embeddings(progress: gr.Progress = gr.Progress()) -> str:
    """Rebuilds the vector database from the current index."""
    if not config.index_path.exists():
        return "Kein Index gefunden."

    try:
        progress(0, desc="Lade Index und erstelle Chunks...")
        chunks = chunk_markdown(config.index_path)
        if not chunks:
            return "Keine Chunks im Index gefunden."

        progress(0.1, desc="Initialisiere Embedder...")
        embedder = Embedder()
        retriever = Retriever(persist_directory=config.embeddings_path)
        retriever.clear()

        texts = [c["content"] for c in chunks]
        batch_size = 32
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in range(0, len(texts), batch_size):
            batch_num = i // batch_size
            progress(
                (batch_num / total_batches) * 0.8 + 0.1, desc=f"Erstelle Embeddings (Batch {batch_num + 1}/{total_batches})..."
            )
            batch_texts = texts[i : i + batch_size]
            batch_chunks = chunks[i : i + batch_size]
            batch_embeddings = embedder.embed_documents(batch_texts)
            retriever.add_chunks(batch_chunks, batch_embeddings)

        progress(1.0, desc="Fertig!")

        # Re-initialize the pipeline and operations
        global pipeline, operations
        try:
            pipeline = RAGPipeline()
            operations = BackupOperations(index_path=config.index_path, rag_pipeline=pipeline)
        except Exception:
            pass

        return "Embeddings erfolgreich erstellt."
    except Exception as e:
        logger.exception("Error rebuilding embeddings")
        return f"Fehler beim Erstellen der Embeddings: {e}"


# UI Definition
with gr.Blocks(title="Semantic Backup Explorer", theme=gr.themes.Soft()) as demo:
    with gr.Group():
        gr.Markdown(
            """
        # 📦 Semantic Backup Explorer

        Willkommen beim Semantic Backup Explorer! Dieses Tool hilft dir dabei, deine Backups auf externen Laufwerken einfach und intelligent zu verwalten.

        - **One-Click Sync**: Vergleiche lokale Ordner blitzschnell mit ihrem Backup und sichere fehlende Dateien mit nur einem Klick.
        - **Index-Erstellung**: Erfasse die Struktur deiner Backup-Laufwerke, um sie auch ohne angeschlossene Festplatte zu durchsuchen.
        - **Semantische Suche (Optional)**: Finde Ordner anhand ihres Inhalts, auch wenn du den genauen Namen vergessen hast.

        *Tipp: Wähle zuerst deinen lokalen Ordner im Tab 'One-Click Sync' aus oder erstelle einen Index im Tab 'Index Viewer'.*
        """
        )

    with gr.Tab("🔄 One-Click Sync") as sync_tab:
        gr.Markdown("### Lokalen Ordner mit Backup vergleichen und synchronisieren")

        gr.Markdown(
            """
            *Hinweis: Der Vergleich erfolgt gegen den gespeicherten **Backup-Index**.
            Dies ermöglicht einen schnellen Abgleich, ohne dass die Festplatte während der Analyse dauerhaft beansprucht wird.
            Stelle sicher, dass der Index aktuell ist.*
            """
        )

        index_info_box = gr.HTML(value=get_index_status_html())

        with gr.Group():
            with gr.Row():
                local_path_display = gr.Textbox(
                    label="Ausgewählter lokaler Ordner",
                    placeholder="Klicke auf 'Ordner wählen'...",
                    interactive=False,
                    info="Der Ordner auf deinem Computer, den du sichern möchtest.",
                    scale=4,
                )
                browse_local_btn = gr.Button("📁 Ordner wählen", scale=1)

            compare_button = gr.Button("🔍 Vergleichen", variant="primary")

        browse_local_btn.click(select_folder, outputs=local_path_display)

        backup_found_info = gr.Markdown()
        target_root_state = gr.State()

        with gr.Row():
            only_local_out = gr.Textbox(
                label="🔴 Nur Lokal",
                lines=10,
                info="Diese Dateien fehlen im Backup oder sind lokal neuer.",
            )
            only_backup_out = gr.Textbox(
                label="🔵 Nur im Backup",
                lines=10,
                info="Diese Dateien existieren nur auf dem Backup-Laufwerk.",
            )
            in_both_out = gr.Textbox(
                label="🟢 Synchron",
                lines=10,
                info="Diese Dateien sind auf beiden Seiten identisch.",
            )

        compare_button.click(
            folder_compare,
            inputs=local_path_display,
            outputs=[backup_found_info, only_local_out, only_backup_out, in_both_out, target_root_state],
        )

        with gr.Group():
            sync_button = gr.Button("🔄 Synchronisieren", variant="secondary")
            gr.Markdown("*Kopiert alle Dateien aus der Liste 'Nur Lokal' in den entsprechenden Backup-Ordner.*")
            sync_status = gr.Textbox(label="Sync Status")

        sync_button.click(run_sync, inputs=[only_local_out, local_path_display, target_root_state], outputs=sync_status)

        sync_tab.select(get_index_status_html, outputs=index_info_box)

    with gr.Tab("📄 Index Viewer"):
        gr.Markdown("### Backup-Index verwalten")
        with gr.Group():
            with gr.Row():
                backup_path_display = gr.Textbox(
                    label="Backup Pfad zum Scannen",
                    placeholder="Wähle das Hauptverzeichnis deines Backup-Laufwerks...",
                    interactive=False,
                    info="Das Verzeichnis, das indiziert werden soll (z.B. Laufwerk E:).",
                    scale=4,
                )
                browse_backup_btn = gr.Button("📁 Ordner wählen", scale=1)

            create_index_button = gr.Button("⚡ Index erstellen", variant="primary")

        browse_backup_btn.click(select_folder, outputs=backup_path_display)

        index_status = gr.Textbox(label="Status")
        with gr.Row():
            refresh_button = gr.Button("🔄 Ansicht aktualisieren")
        index_content = gr.Textbox(
            label="Inhalt von backup_index.md",
            lines=20,
            value=get_index_viewer(),
            info="Hier siehst du die aktuelle Liste aller indizierten Dateien und Ordner.",
        )

        create_index_button.click(create_index, inputs=backup_path_display, outputs=[index_status, index_content]).then(
            get_index_status_html, outputs=index_info_box
        )
        refresh_button.click(get_index_viewer, inputs=[], outputs=index_content)

    with gr.Tab("📚 Semantic Search") as semantic_search_tab:
        gr.Markdown("### Durchsuche dein Backup mit natürlicher Sprache")

        gr.Markdown(
            """
            ⚠️ **Datenschutz-Hinweis**: Bei der semantischen Suche werden relevante Teile deiner Pfadnamen an ein LLM in der Cloud (Groq) gesendet.
            Nutze diese Funktion nicht, wenn deine Pfadnamen sensible Informationen enthalten.
            """
        )

        if pipeline is None:
            gr.Markdown(
                "⚠️ **Semantische Suche deaktiviert**: Die benötigten Python-Pakete sind nicht installiert. "
                "Bitte installiere sie mit `pip install -e .[semantic]`, um diese Funktion zu nutzen."
            )
            embeddings_warning = gr.Markdown(visible=False)
            rebuild_embeddings_button = gr.Button(visible=False)
            query_input = gr.Textbox(visible=False)
            search_button = gr.Button(visible=False)
            answer_output = gr.Textbox(visible=False)
            context_output = gr.Textbox(visible=False)
        else:
            with gr.Group():
                embeddings_warning = gr.Markdown(visible=False)
                rebuild_embeddings_button = gr.Button(
                    "Embeddings erstellen / aktualisieren",
                    visible=False,
                    variant="secondary",
                )

            with gr.Row():
                query_input = gr.Textbox(
                    label="Deine Frage",
                    placeholder="z.B. Wo liegen meine alten Steuererklärungen?",
                    info="Frage nach Inhalten, Projekten oder Dokumenten.",
                    scale=4,
                )
                search_button = gr.Button("🔍 Suchen", variant="primary", scale=1)

            with gr.Row():
                with gr.Column(scale=1):
                    answer_output = gr.Textbox(label="KI-Antwort", lines=5)
                with gr.Column(scale=1):
                    context_output = gr.Textbox(
                        label="Gefundene Ordner (Kontext)",
                        lines=10,
                        info="Diese Ordner wurden als relevant für deine Suche identifiziert.",
                    )

            search_button.click(semantic_search, inputs=query_input, outputs=[answer_output, context_output])

            semantic_search_tab.select(check_embeddings_staleness, outputs=[embeddings_warning, rebuild_embeddings_button])
            rebuild_embeddings_button.click(run_rebuild_embeddings, outputs=[]).then(
                check_embeddings_staleness, outputs=[embeddings_warning, rebuild_embeddings_button]
            )

    demo.load(
        check_embeddings_staleness, outputs=[embeddings_warning, rebuild_embeddings_button]
    ).then(get_index_status_html, outputs=index_info_box)


def main() -> None:
    """Launches the Gradio application."""
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)


if __name__ == "__main__":
    main()
