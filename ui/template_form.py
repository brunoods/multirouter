# ui/template_form.py
import tkinter as tk
from tkinter import ttk, messagebox

class TemplateForm(tk.Toplevel):
    """Janela de formulário gerada dinamicamente para preencher variáveis de um template."""
    def __init__(self, parent, variables):
        super().__init__(parent)
        self.transient(parent)
        self.title("Preencher Variáveis do Template")
        
        self.result = None
        self.entries = {}

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill="both", expand=True)

        # Cria um Label e um Entry para cada variável encontrada
        for i, var_name in enumerate(variables):
            ttk.Label(form_frame, text=f"{var_name}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.entries[var_name] = entry

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Aplicar", command=self.on_apply).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=10)

    def on_apply(self):
        """Coleta os valores dos campos e fecha a janela."""
        self.result = {var_name: entry.get() for var_name, entry in self.entries.items()}
        
        # Validação simples para garantir que nenhum campo ficou vazio
        if any(not value for value in self.result.values()):
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todas as variáveis.", parent=self)
            self.result = None # Anula o resultado se a validação falhar
            return
            
        self.destroy()