# ui/mass_commands_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from logic.mass_commands import run_mass_commands

class MassCommandsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.device_vars = {}

        # --- Frame Principal ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) # Dá mais espaço à área de resultados

        # --- Frame de Seleção de Dispositivos (Esquerda) ---
        selection_frame = ttk.LabelFrame(main_frame, text="1. Selecionar Dispositivos")
        selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.device_list_frame = ttk.Frame(selection_frame)
        self.device_list_frame.pack(fill="both", expand=True)

        # --- Frame de Comando e Ação (Centro) ---
        action_frame = ttk.LabelFrame(main_frame, text="2. Inserir Comando e Executar")
        action_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        ttk.Label(action_frame, text="Comando(s) a executar:").pack(anchor="w", padx=5, pady=5)
        self.command_entry = scrolledtext.ScrolledText(action_frame, height=5, wrap=tk.WORD, font=("Consolas", 9))
        self.command_entry.pack(fill="x", expand=True, padx=5)
        self.command_entry.insert("1.0", "show version")

        self.run_button = ttk.Button(action_frame, text="Executar nos Dispositivos Selecionados", command=lambda: run_mass_commands(self.controller))
        self.run_button.pack(pady=10)

        # --- Frame de Resultados (Abaixo) ---
        results_frame = ttk.LabelFrame(main_frame, text="3. Resultados")
        results_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD, font=("Consolas", 9), state="normal", background="#ffffff")
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)

    def populate_device_list(self):
        """Preenche a lista de checkboxes com os dispositivos do inventário."""
        # Limpa widgets antigos
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()
        
        self.device_vars.clear()
        inventory = self.controller.inventory
        
        for device in inventory:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.device_list_frame, text=device['name'], variable=var)
            cb.pack(anchor="w", padx=10, pady=2)
            self.device_vars[device['id']] = var