from semantic_backup_explorer.utils.compatibility import check_python_version
check_python_version()

import gradio as gr
import os
from pathlib import Path
from semantic_backup_explorer.rag.rag_pipeline import RAGPipeline
from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.sync.sync_missing import sync_files
from semantic_backup_explorer.chunking.folder_chunker import chunk_markdown

# Initialize RAG Pipeline
# Note: This might fail if GROQ_API_KEY is not set,
# but we'll handle it or assume it's set in the environment.
try:
    pipeline = RAGPipeline()
except Exception as e:
    print(f"Warning: Could not initialize RAG Pipeline: {e}")
    pipeline = None

def semantic_search(query):
    if not pipeline:
        return "RAG Pipeline not initialized. Check GROQ_API_KEY.", ""
    answer, context = pipeline.answer_question(query)
    return answer, context

def folder_compare(local_path):
    if not local_path or not os.path.exists(local_path):
        return "Ungültiger Pfad.", "", ""

    # Try to find corresponding folder in backup using RAG
    # We use the folder name as a query
    folder_name = os.path.basename(local_path)
    if pipeline:
        _, context = pipeline.answer_question(f"Wo ist der Ordner {folder_name}?")
        # Extract the first folder path from context (starts with ## )
        import re
        match = re.search(r'## (.*)', context)
        if match:
            backup_folder = match.group(1).strip()
            # Get files from the retrieved chunk
            backup_files = []
            for line in context.split('\n'):
                if line.startswith('- '):
                    file_path = line.replace('- ', '').strip()
                    # Make it relative to the backup folder
                    try:
                        rel_path = os.path.relpath(file_path, backup_folder)
                        backup_files.append(rel_path)
                    except:
                        pass

            diff = compare_folders(local_path, backup_files)

            only_local = "\n".join(diff["only_local"])
            only_backup = "\n".join(diff["only_backup"])
            in_both = "\n".join(diff["in_both"])

            return f"Gefundenes Backup: {backup_folder}", only_local, only_backup, in_both, backup_folder

    return "Kein passendes Backup gefunden.", "", "", "", ""

def run_sync(only_local_text, local_root, target_root):
    if not target_root or not os.path.exists(target_root):
        return "Zielordner existiert nicht oder ist nicht angeschlossen."

    files_to_sync = [f.strip() for f in only_local_text.split('\n') if f.strip()]
    if not files_to_sync:
        return "Keine Dateien zum Synchronisieren."

    synced, errors = sync_files(files_to_sync, local_root, target_root)

    msg = f"{len(synced)} Dateien erfolgreich kopiert."
    if errors:
        msg += f"\nFehler bei {len(errors)} Dateien."
    return msg

def get_index_viewer():
    index_path = "data/backup_index.md"
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Kein Index gefunden. Bitte zuerst `scripts/build_index.py` ausführen."

with gr.Blocks(title="Semantic Backup Explorer") as demo:
    gr.Markdown("# 📦 Semantic Backup Explorer")

    with gr.Tab("📚 Semantic Search"):
        with gr.Row():
            query_input = gr.Textbox(label="Frage an dein Backup", placeholder="Wo liegen alte Steuerunterlagen?")
            search_button = gr.Button("Suchen")
        answer_output = gr.Textbox(label="Antwort")
        context_output = gr.Textbox(label="Gefundene Ordner (Kontext)", lines=10)
        search_button.click(semantic_search, inputs=query_input, outputs=[answer_output, context_output])

    with gr.Tab("📂 Folder Compare"):
        local_path_input = gr.Textbox(label="Lokaler Ordner Pfad")
        compare_button = gr.Button("Vergleichen")

        backup_found_info = gr.Markdown()
        target_root_state = gr.State()

        with gr.Row():
            only_local_out = gr.Textbox(label="🔴 Nur Lokal (Fehlt im Backup)", lines=10)
            only_backup_out = gr.Textbox(label="🔵 Nur im Backup", lines=10)
            in_both_out = gr.Textbox(label="🟢 In beiden vorhanden", lines=10)

        compare_button.click(folder_compare, inputs=local_path_input,
                             outputs=[backup_found_info, only_local_out, only_backup_out, in_both_out, target_root_state])

        sync_button = gr.Button("🔄 Synchronisieren (Fehlende Dateien kopieren)")
        sync_status = gr.Textbox(label="Sync Status")
        sync_button.click(run_sync, inputs=[only_local_out, local_path_input, target_root_state], outputs=sync_status)

    with gr.Tab("📄 Index Viewer"):
        refresh_button = gr.Button("Aktualisieren")
        index_content = gr.Textbox(label="backup_index.md", lines=20, value=get_index_viewer())
        refresh_button.click(get_index_viewer, inputs=[], outputs=index_content)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
