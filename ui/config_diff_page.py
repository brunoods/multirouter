"""
Página da interface do utilizador para a comparação de ficheiros de configuração.
"""

from tkinter import ttk, filedialog
from ttkbootstrap.scrolled import ScrolledText
from logic.diff_manager import compare_configs


class ConfigDiffPage(ttk.Frame):
    """Frame que contém os widgets para a comparação de configurações."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.file1_content = ""
        self.file2_content = ""

        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Botões para carregar ficheiros
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 10))

        btn_file1 = ttk.Button(
            btn_frame, text="Carregar Ficheiro 1", command=self.load_file1
        )
        btn_file1.pack(side="left", padx=5)

        btn_file2 = ttk.Button(
            btn_frame, text="Carregar Ficheiro 2", command=self.load_file2
        )
        btn_file2.pack(side="left", padx=5)

        btn_compare = ttk.Button(
            btn_frame,
            text="Comparar",
            command=self.perform_comparison,
            bootstyle="success",
        )
        btn_compare.pack(side="left", padx=5)

        # Labels para os nomes dos ficheiros
        self.lbl_file1 = ttk.Label(btn_frame, text="Nenhum ficheiro carregado")
        self.lbl_file1.pack(side="left", padx=10)

        self.lbl_file2 = ttk.Label(btn_frame, text="Nenhum ficheiro carregado")
        self.lbl_file2.pack(side="left", padx=10)

        # Área de texto para exibir as diferenças
        self.diff_text = ScrolledText(main_frame, wrap="word", height=20)
        self.diff_text.pack(fill="both", expand=True)

    def load_file1(self):
        """Carrega o conteúdo do primeiro ficheiro."""
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r") as f:
                self.file1_content = f.read()
            self.lbl_file1.config(text=filepath.split("/")[-1])

    def load_file2(self):
        """Carrega o conteúdo do segundo ficheiro."""
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r") as f:
                self.file2_content = f.read()
            self.lbl_file2.config(text=filepath.split("/")[-1])

    def perform_comparison(self):
        """Executa a comparação e exibe o resultado."""
        diff_result = compare_configs(self.file1_content, self.file2_content)
        self.diff_text.delete("1.0", "end")
        self.diff_text.insert("1.0", diff_result)
