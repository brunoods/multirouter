# logic/diff_manager.py
"""
Módulo para a lógica de comparação de configurações (diff).
"""
import difflib
from tkinter import filedialog, messagebox


def load_file_into_text_widget(text_widget):
    """Abre uma janela para selecionar um ficheiro e carrega o seu conteúdo num widget de texto."""
    filepath = filedialog.askopenfilename(
        title="Selecionar ficheiro de configuração",
        filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Ficheiros", "*.*")],
    )
    if not filepath:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", content)
    except Exception as e:
        messagebox.showerror(
            "Erro ao Ler Ficheiro", f"Não foi possível ler o ficheiro:\n{e}"
        )


def compare_configs(app):
    """Compara o texto dos dois painéis na página de Diff e exibe o resultado."""
    diff_page = app.frames[app.pages["ConfigDiffPage"]]

    config_a = diff_page.text_a.get("1.0", "end-1c").splitlines()
    config_b = diff_page.text_b.get("1.0", "end-1c").splitlines()

    # Gera as diferenças
    diff = difflib.unified_diff(
        config_a,
        config_b,
        fromfile="Configuração A",
        tofile="Configuração B",
        lineterm="",
    )

    # Limpa a área de resultados e prepara as tags de cor
    results_text = diff_page.results_text
    results_text.config(state="normal")
    results_text.delete("1.0", "end")
    results_text.tag_configure("addition", foreground="green")
    results_text.tag_configure("removal", foreground="red")
    results_text.tag_configure(
        "header", foreground="blue", font=("Consolas", 9, "bold")
    )

    # Exibe o resultado com cores
    for line in diff:
        if line.startswith("+"):
            results_text.insert("end", line + "\n", "addition")
        elif line.startswith("-"):
            results_text.insert("end", line + "\n", "removal")
        elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            results_text.insert("end", line + "\n", "header")
        else:
            results_text.insert("end", line + "\n")

    results_text.config(state="disabled")
    app.status_label.config(text="Comparação concluída.")
